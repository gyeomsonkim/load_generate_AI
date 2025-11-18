"""
지도 관련 API 엔드포인트
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import logging
import uuid
import aiofiles

from app.models.schemas import MapUploadRequest, MapResponse, MapPreprocessingRequest, MapPreprocessingResponse
from app.models.database import Map, PreprocessedMapData
from app.models.enums import MapStatus
from app.services.storage_service import StorageService
from app.core.pathfinding.preprocessor import MapPreprocessor
from app.services.ml_service import get_ml_service, ProcessingMode
from app.api.dependencies import get_db, get_storage_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/maps", tags=["maps"])


@router.post("/upload", response_model=MapResponse)
async def upload_map(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    map_type: str = Form("other"),
    scale_meters_per_pixel: float = Form(1.0),
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """
    지도 이미지 업로드 및 전처리 시작

    - 이미지 파일을 업로드합니다
    - DB에 메타데이터를 저장합니다
    - 백그라운드에서 전처리를 시작합니다
    """
    # 파일 검증
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다")

    if file.size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기가 너무 큽니다 (최대: {settings.max_upload_size // 1024 // 1024}MB)"
        )

    try:
        # 파일 읽기
        file_content = await file.read()

        # 스토리지에 저장
        file_path, metadata = await storage.save_uploaded_image(file_content, file.filename)

        # DB에 맵 정보 저장
        map_id = str(uuid.uuid4())
        new_map = Map(
            id=map_id,
            name=name,
            description=description,
            map_type=map_type,
            original_image_path=file_path,
            width=metadata['width'],
            height=metadata['height'],
            scale_meters_per_pixel=scale_meters_per_pixel,
            preprocessing_status=MapStatus.UPLOADED.value,
            preprocessing_metadata=metadata
        )

        db.add(new_map)
        await db.commit()
        await db.refresh(new_map)

        # 백그라운드에서 전처리 시작
        background_tasks.add_task(
            preprocess_map_task,
            map_id,
            file_path,
            storage
        )

        logger.info(f"지도 업로드 성공: {map_id}")

        # Response 생성
        return MapResponse(
            id=new_map.id,
            name=new_map.name,
            description=new_map.description,
            map_type=new_map.map_type,
            width=new_map.width,
            height=new_map.height,
            scale_meters_per_pixel=new_map.scale_meters_per_pixel,
            preprocessing_status=new_map.preprocessing_status,
            original_image_url=storage.get_file_url(file_path),
            created_at=new_map.created_at,
            updated_at=new_map.updated_at
        )

    except Exception as e:
        logger.error(f"지도 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{map_id}/preprocess", response_model=MapPreprocessingResponse)
async def preprocess_map(
    map_id: str,
    request: MapPreprocessingRequest,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """
    지도 전처리 실행 (수동)

    특정 지도의 전처리를 수동으로 실행합니다.
    """
    # 지도 조회
    from sqlalchemy import select
    result = await db.execute(select(Map).where(Map.id == map_id))
    map_obj = result.scalar_one_or_none()

    if not map_obj:
        raise HTTPException(status_code=404, detail="지도를 찾을 수 없습니다")

    # 이미 처리중인지 확인
    if map_obj.preprocessing_status == MapStatus.PROCESSING.value:
        raise HTTPException(status_code=409, detail="이미 처리 중입니다")

    # 재처리 옵션 확인
    if not request.force_reprocess and map_obj.preprocessing_status == MapStatus.PROCESSED.value:
        return MapPreprocessingResponse(
            map_id=map_id,
            status="already_processed",
            processing_time=0,
            walkable_area_percentage=map_obj.preprocessing_metadata.get('walkable_percentage', 0),
            detected_obstacles=map_obj.preprocessing_metadata.get('obstacle_count', 0),
            detected_entrances=len(map_obj.preprocessing_metadata.get('entrance_points', [])),
            message="이미 처리된 지도입니다"
        )

    try:
        # 전처리 실행
        result = await preprocess_map_task(map_id, map_obj.original_image_path, storage)

        return MapPreprocessingResponse(
            map_id=map_id,
            status="completed",
            processing_time=result['processing_time'],
            walkable_area_percentage=result['walkable_percentage'],
            detected_obstacles=result['obstacle_count'],
            detected_entrances=len(result.get('entrance_points', [])),
            message="전처리가 완료되었습니다"
        )

    except Exception as e:
        logger.error(f"전처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"전처리 실패: {str(e)}")


async def preprocess_map_task(map_id: str, image_path: str, storage: StorageService):
    """
    백그라운드에서 실행되는 전처리 작업
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from app.config import settings
    import json

    # 비동기 DB 세션 생성
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as db:
        try:
            # 상태를 처리중으로 변경
            from sqlalchemy import update
            await db.execute(
                update(Map).where(Map.id == map_id).values(
                    preprocessing_status=MapStatus.PROCESSING.value
                )
            )
            await db.commit()

            # 출력 디렉토리 생성
            output_dir = Path(settings.storage_path) / "processed" / map_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # S3 모드일 때 파일 다운로드
            local_image_path = image_path
            if storage.storage_type == "s3":
                # S3에서 파일 다운로드
                image_content = await storage.get_file(image_path)

                # 로컬 임시 파일로 저장
                temp_dir = Path(settings.storage_path) / "temp"
                temp_dir.mkdir(parents=True, exist_ok=True)
                local_image_path = str(temp_dir / Path(image_path).name)

                async with aiofiles.open(local_image_path, 'wb') as f:
                    await f.write(image_content)

                logger.info(f"S3 파일 다운로드 완료: {image_path} -> {local_image_path}")

            # ML 서비스를 통한 전처리 실행 (ML + CV 통합)
            ml_service = get_ml_service()
            result = await ml_service.preprocess_map(
                image_path=local_image_path,
                output_dir=str(output_dir),
                mode=None,  # 자동 선택
                user_id=map_id
            )

            # 결과에서 알고리즘 결정
            algorithm_used = result.get('method', 'cv')
            if result.get('processing_mode') == 'hybrid':
                algorithm_used = f"hybrid_{result.get('selected_method', 'cv')}"

            # S3 모드일 때 전처리 결과를 S3에 업로드
            s3_paths = {}
            if storage.storage_type == "s3":
                processed_files = {
                    'binary_image': result.get('binary_image'),
                    'edge_image': result.get('edge_image'),
                    'walkable_mask': result.get('walkable_mask_path') or result.get('walkable_mask'),
                    'visualization': result.get('visualization'),
                    'navigation_grid': result.get('navigation_grid_path')
                }

                for file_type, file_path in processed_files.items():
                    if file_path and Path(file_path).exists():
                        # 파일 읽기
                        async with aiofiles.open(file_path, 'rb') as f:
                            file_content = await f.read()

                        # S3에 업로드
                        s3_key = await storage.save_processed_data(
                            map_id=map_id,
                            data_type=file_type,
                            data=file_content
                        )
                        s3_paths[file_type] = s3_key
                        logger.info(f"Uploaded {file_type} to S3: {s3_key}")

            # PreprocessedMapData 저장 (S3 경로 또는 로컬 경로)
            # 그리드 데이터 로드 (navigation_grid_path 또는 navigation_grid 키 지원)
            grid_data = None
            grid_path = result.get('navigation_grid_path') or result.get('navigation_grid')
            if grid_path and Path(grid_path).exists():
                try:
                    with open(grid_path, 'r') as f:
                        grid_data = json.load(f)
                    logger.info(f"Grid data loaded from: {grid_path}")
                except Exception as e:
                    logger.error(f"Failed to load grid data from {grid_path}: {e}")

            preprocessed_data = PreprocessedMapData(
                map_id=map_id,
                binary_image_path=s3_paths.get('binary_image') if s3_paths else result.get('binary_image'),
                edge_image_path=s3_paths.get('edge_image') if s3_paths else result.get('edge_image'),
                segmented_image_path=s3_paths.get('walkable_mask') if s3_paths else (result.get('walkable_mask_path') or result.get('walkable_mask')),
                graph_data=None,  # Phase 2에서 구현
                walkable_grid=grid_data,
                entrance_points=result.get('entrance_points'),
                processing_time=result['processing_time'],
                algorithm_used=algorithm_used
            )

            # 기존 전처리 데이터 삭제
            from sqlalchemy import delete
            await db.execute(delete(PreprocessedMapData).where(PreprocessedMapData.map_id == map_id))

            # 새 데이터 저장
            db.add(preprocessed_data)

            # Map 테이블 업데이트
            await db.execute(
                update(Map).where(Map.id == map_id).values(
                    preprocessing_status=MapStatus.PROCESSED.value,
                    processed_image_path=s3_paths.get('visualization') if s3_paths else result.get('visualization'),
                    preprocessing_metadata=result,
                    walkable_areas=result.get('walkable_percentage'),
                    obstacles=result.get('obstacles')
                )
            )

            await db.commit()
            logger.info(f"지도 전처리 완료: {map_id}")

            return result

        except Exception as e:
            logger.error(f"전처리 작업 실패: {e}")

            # 실패 상태로 변경
            await db.execute(
                update(Map).where(Map.id == map_id).values(
                    preprocessing_status=MapStatus.FAILED.value,
                    preprocessing_metadata={'error': str(e)}
                )
            )
            await db.commit()
            raise


@router.get("/{map_id}", response_model=MapResponse)
async def get_map(
    map_id: str,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """특정 지도 정보 조회"""
    from sqlalchemy import select

    result = await db.execute(select(Map).where(Map.id == map_id))
    map_obj = result.scalar_one_or_none()

    if not map_obj:
        raise HTTPException(status_code=404, detail="지도를 찾을 수 없습니다")

    return MapResponse(
        id=map_obj.id,
        name=map_obj.name,
        description=map_obj.description,
        map_type=map_obj.map_type,
        width=map_obj.width,
        height=map_obj.height,
        scale_meters_per_pixel=map_obj.scale_meters_per_pixel,
        preprocessing_status=map_obj.preprocessing_status,
        original_image_url=storage.get_file_url(map_obj.original_image_path) if map_obj.original_image_path else None,
        processed_image_url=storage.get_file_url(map_obj.processed_image_path) if map_obj.processed_image_path else None,
        created_at=map_obj.created_at,
        updated_at=map_obj.updated_at
    )


@router.get("/", response_model=List[MapResponse])
async def list_maps(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
):
    """업로드된 모든 지도 목록 조회"""
    from sqlalchemy import select

    result = await db.execute(
        select(Map).offset(skip).limit(limit).order_by(Map.created_at.desc())
    )
    maps = result.scalars().all()

    return [
        MapResponse(
            id=m.id,
            name=m.name,
            description=m.description,
            map_type=m.map_type,
            width=m.width,
            height=m.height,
            scale_meters_per_pixel=m.scale_meters_per_pixel,
            preprocessing_status=m.preprocessing_status,
            original_image_url=storage.get_file_url(m.original_image_path) if m.original_image_path else None,
            processed_image_url=storage.get_file_url(m.processed_image_path) if m.processed_image_path else None,
            created_at=m.created_at,
            updated_at=m.updated_at
        )
        for m in maps
    ]