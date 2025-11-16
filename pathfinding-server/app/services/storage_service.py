"""
파일 스토리지 서비스
로컬 파일 시스템 또는 MinIO를 사용한 이미지 저장
"""
import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import aiofiles
import uuid
from minio import Minio
from minio.error import S3Error
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """파일 스토리지 서비스"""

    def __init__(self, storage_type: str = "local", config: dict = None):
        self.storage_type = storage_type
        self.config = config or {}

        if storage_type == "local":
            self.base_path = Path(self.config.get("storage_path", "./storage"))
            self.base_path.mkdir(parents=True, exist_ok=True)
            self.uploads_path = self.base_path / "uploads"
            self.processed_path = self.base_path / "processed"
            self.uploads_path.mkdir(exist_ok=True)
            self.processed_path.mkdir(exist_ok=True)
        elif storage_type == "minio":
            self.client = Minio(
                self.config.get("minio_endpoint", "localhost:9000"),
                access_key=self.config.get("minio_access_key", "minioadmin"),
                secret_key=self.config.get("minio_secret_key", "minioadmin"),
                secure=self.config.get("minio_secure", False)
            )
            self.bucket = self.config.get("minio_bucket", "pathfinding-maps")
            self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """MinIO 버킷 존재 확인 및 생성"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"버킷 생성됨: {self.bucket}")
        except S3Error as e:
            logger.error(f"버킷 생성 실패: {e}")
            raise

    async def save_uploaded_image(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        """
        업로드된 이미지 저장

        Returns:
            (저장 경로, 이미지 메타데이터)
        """
        # 파일명 안전하게 처리
        safe_filename = self._generate_safe_filename(filename)
        file_id = str(uuid.uuid4())
        extension = Path(filename).suffix.lower()

        if self.storage_type == "local":
            # 로컬 저장
            file_path = self.uploads_path / f"{file_id}{extension}"

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)

            # 이미지 메타데이터 추출
            metadata = self._extract_image_metadata(str(file_path))

            # 썸네일 생성
            thumbnail_path = await self._create_thumbnail(str(file_path), file_id)
            metadata['thumbnail_path'] = str(thumbnail_path)

            return str(file_path), metadata

        else:  # MinIO
            object_name = f"uploads/{file_id}{extension}"

            # MinIO에 업로드
            from io import BytesIO
            self.client.put_object(
                self.bucket,
                object_name,
                BytesIO(file_content),
                len(file_content)
            )

            # 메타데이터 추출 (임시 파일 사용)
            temp_path = f"/tmp/{file_id}{extension}"
            with open(temp_path, 'wb') as f:
                f.write(file_content)

            metadata = self._extract_image_metadata(temp_path)
            os.remove(temp_path)

            return object_name, metadata

    def _generate_safe_filename(self, filename: str) -> str:
        """안전한 파일명 생성"""
        # 특수문자 제거
        import re
        safe = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return safe

    def _extract_image_metadata(self, image_path: str) -> dict:
        """이미지 메타데이터 추출"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode

                return {
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'mode': mode,
                    'size_bytes': os.path.getsize(image_path),
                    'aspect_ratio': width / height if height > 0 else 0
                }
        except Exception as e:
            logger.error(f"메타데이터 추출 실패: {e}")
            return {
                'width': 0,
                'height': 0,
                'format': 'unknown',
                'error': str(e)
            }

    async def _create_thumbnail(self, image_path: str, file_id: str, size: Tuple[int, int] = (256, 256)) -> Path:
        """썸네일 생성"""
        thumbnail_path = self.uploads_path / f"{file_id}_thumb.jpg"

        try:
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, "JPEG", quality=85)

            return thumbnail_path
        except Exception as e:
            logger.error(f"썸네일 생성 실패: {e}")
            return Path(image_path)  # 실패 시 원본 경로 반환

    async def save_processed_data(self, map_id: str, data_type: str, data: bytes) -> str:
        """
        전처리된 데이터 저장

        Args:
            map_id: 지도 ID
            data_type: 데이터 유형 (binary, edges, walkable, grid 등)
            data: 저장할 데이터

        Returns:
            저장 경로
        """
        if self.storage_type == "local":
            # 맵별 디렉토리 생성
            map_dir = self.processed_path / map_id
            map_dir.mkdir(exist_ok=True)

            # 파일 저장
            file_path = map_dir / f"{data_type}.png"

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(data)

            return str(file_path)

        else:  # MinIO
            object_name = f"processed/{map_id}/{data_type}.png"

            from io import BytesIO
            self.client.put_object(
                self.bucket,
                object_name,
                BytesIO(data),
                len(data)
            )

            return object_name

    async def get_file(self, file_path: str) -> bytes:
        """파일 읽기"""
        if self.storage_type == "local":
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        else:  # MinIO
            response = self.client.get_object(self.bucket, file_path)
            return response.read()

    async def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        try:
            if self.storage_type == "local":
                os.remove(file_path)
            else:  # MinIO
                self.client.remove_object(self.bucket, file_path)
            return True
        except Exception as e:
            logger.error(f"파일 삭제 실패: {e}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """파일 접근 URL 생성"""
        if self.storage_type == "local":
            # 로컬의 경우 상대 경로 반환
            return f"/files/{Path(file_path).relative_to(self.base_path)}"
        else:  # MinIO
            # 사전 서명된 URL 생성 (1시간 유효)
            from datetime import timedelta
            return self.client.presigned_get_object(
                self.bucket,
                file_path,
                expires=timedelta(hours=1)
            )