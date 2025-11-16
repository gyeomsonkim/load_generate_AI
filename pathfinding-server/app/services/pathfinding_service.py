"""
길찾기 서비스 레이어
A* 알고리즘과 경로 최적화를 통합하여 실제 길찾기 기능 제공
"""
import json
import time
import hashlib
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import numpy as np
import logging
from datetime import datetime
import uuid

from app.core.pathfinding.astar import AStarPathfinder
from app.core.pathfinding.optimizer import PathOptimizer
from app.models.database import Map, PreprocessedMapData, PathfindingRequest
from app.models.enums import PathDifficulty
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)


class PathfindingService:
    """
    길찾기 서비스 클래스
    전처리된 지도 데이터를 사용하여 최적 경로를 찾고 반환
    """

    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.astar = AStarPathfinder(diagonal_movement=True, smooth_path=True)
        self.optimizer = PathOptimizer()
        self.cache = {}  # 간단한 메모리 캐시 (실제로는 Redis 사용 권장)

    async def find_route(self, db: AsyncSession, map_id: str,
                        start: Tuple[float, float], end: Tuple[float, float],
                        options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        두 지점 사이의 최적 경로 찾기

        Args:
            db: 데이터베이스 세션
            map_id: 지도 ID
            start: 시작 좌표 (정규화된 0-1 범위)
            end: 종료 좌표 (정규화된 0-1 범위)
            options: 추가 옵션

        Returns:
            경로 정보 딕셔너리
        """
        start_time = time.time()
        options = options or {}

        # 캐시 키 생성
        cache_key = self._generate_cache_key(map_id, start, end, options)

        # 캐시 확인
        if cache_key in self.cache and options.get('use_cache', True):
            logger.info(f"캐시에서 경로 반환: {cache_key}")
            cached_result = self.cache[cache_key].copy()
            cached_result['cached'] = True
            return cached_result

        try:
            # 지도 정보 조회
            map_data = await self._get_map_data(db, map_id)
            if not map_data:
                raise ValueError(f"지도를 찾을 수 없습니다: {map_id}")

            # 전처리된 데이터 조회
            preprocessed_data = await self._get_preprocessed_data(db, map_id)
            if not preprocessed_data:
                raise ValueError(f"전처리된 데이터를 찾을 수 없습니다: {map_id}")

            # 그리드 데이터 로드
            grid = await self._load_grid_data(preprocessed_data)
            if grid is None:
                raise ValueError(f"그리드 데이터를 로드할 수 없습니다: {map_id}")

            # A* 알고리즘으로 경로 찾기
            raw_path = self.astar.find_path(grid, start, end)
            if raw_path is None:
                return {
                    'success': False,
                    'error': '경로를 찾을 수 없습니다',
                    'start': start,
                    'end': end,
                    'map_id': map_id
                }

            # 경로 최적화
            optimized = self.optimizer.optimize_path(raw_path, options)

            # 실제 거리 계산 (미터 단위)
            pixel_distance = optimized['distance'] * max(grid.shape)
            real_distance = pixel_distance * map_data.scale_meters_per_pixel

            # 예상 시간 계산 (보행 속도 5km/h 기준)
            walking_speed = 5000 / 3600  # m/s
            estimated_time = real_distance / walking_speed

            # 난이도 계산
            difficulty = self._calculate_difficulty(optimized, real_distance)

            # 처리 시간
            processing_time = time.time() - start_time

            # 결과 생성
            result = {
                'success': True,
                'path_id': str(uuid.uuid4()),
                'map_id': map_id,
                'start': start,
                'end': end,
                'polyline': optimized['smooth_path'],
                'waypoints': optimized['waypoints'],
                'svg_path': optimized['svg_path'],
                'distance_pixels': pixel_distance,
                'distance_meters': real_distance,
                'estimated_time_seconds': estimated_time,
                'difficulty': difficulty,
                'accessibility_score': self._calculate_accessibility_score(optimized),
                'turn_count': len(optimized['waypoints']) - 2 if len(optimized['waypoints']) > 2 else 0,
                'processing_time': processing_time,
                'cached': False,
                'optimization_stats': optimized['optimization_stats']
            }

            # 결과를 데이터베이스에 저장
            await self._save_pathfinding_request(db, result)

            # 캐시에 저장
            self.cache[cache_key] = result.copy()

            return result

        except Exception as e:
            logger.error(f"경로 찾기 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'start': start,
                'end': end,
                'map_id': map_id,
                'processing_time': time.time() - start_time
            }

    async def find_multi_route(self, db: AsyncSession, map_id: str,
                             points: List[Tuple[float, float]],
                             options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        여러 지점을 경유하는 경로 찾기

        Args:
            db: 데이터베이스 세션
            map_id: 지도 ID
            points: 경유할 지점들 (정규화된 좌표)
            options: 추가 옵션 (optimize_order, return_to_start 등)

        Returns:
            다중 경로 정보
        """
        if len(points) < 2:
            return {
                'success': False,
                'error': '최소 2개 이상의 지점이 필요합니다'
            }

        options = options or {}
        start_time = time.time()

        # 순서 최적화 여부
        if options.get('optimize_order', False) and len(points) > 3:
            points = await self._optimize_waypoint_order(db, map_id, points)

        # 시작점으로 복귀 여부
        if options.get('return_to_start', False):
            points.append(points[0])

        # 각 구간별 경로 찾기
        segments = []
        total_distance = 0
        total_time = 0

        for i in range(len(points) - 1):
            segment_result = await self.find_route(
                db, map_id, points[i], points[i + 1], options
            )

            if not segment_result.get('success'):
                return {
                    'success': False,
                    'error': f"구간 {i+1} 경로를 찾을 수 없습니다",
                    'failed_segment': i,
                    'start': points[i],
                    'end': points[i + 1]
                }

            segments.append({
                'segment_index': i,
                'start': points[i],
                'end': points[i + 1],
                'polyline': segment_result['polyline'],
                'distance': segment_result['distance_meters'],
                'time': segment_result['estimated_time_seconds']
            })

            total_distance += segment_result['distance_meters']
            total_time += segment_result['estimated_time_seconds']

        # 전체 경로 결합
        combined_polyline = []
        for segment in segments:
            if combined_polyline and segment['polyline']:
                # 중복 점 제거
                if combined_polyline[-1] == segment['polyline'][0]:
                    combined_polyline.extend(segment['polyline'][1:])
                else:
                    combined_polyline.extend(segment['polyline'])
            else:
                combined_polyline.extend(segment['polyline'])

        return {
            'success': True,
            'path_id': str(uuid.uuid4()),
            'map_id': map_id,
            'points': points,
            'segments': segments,
            'combined_polyline': combined_polyline,
            'total_distance_meters': total_distance,
            'total_time_seconds': total_time,
            'segment_count': len(segments),
            'processing_time': time.time() - start_time
        }

    async def find_alternative_routes(self, db: AsyncSession, map_id: str,
                                     start: Tuple[float, float], end: Tuple[float, float],
                                     max_alternatives: int = 3) -> Dict[str, Any]:
        """
        대체 경로 찾기

        Args:
            db: 데이터베이스 세션
            map_id: 지도 ID
            start: 시작 좌표
            end: 종료 좌표
            max_alternatives: 최대 대체 경로 수

        Returns:
            주 경로와 대체 경로들
        """
        start_time = time.time()
        alternatives = []

        # 메인 경로 찾기
        main_route = await self.find_route(db, map_id, start, end)
        if not main_route.get('success'):
            return main_route

        alternatives.append({
            'type': 'optimal',
            'description': '최적 경로',
            **main_route
        })

        # 대체 경로 생성 전략
        # 1. 대각선 이동 비활성화
        if len(alternatives) < max_alternatives:
            self.astar.diagonal_movement = False
            alt_route = await self.find_route(
                db, map_id, start, end,
                {'use_cache': False, 'smoothing_level': 'low'}
            )
            if alt_route.get('success') and alt_route['polyline'] != main_route['polyline']:
                alternatives.append({
                    'type': 'no_diagonal',
                    'description': '직각 이동 경로',
                    **alt_route
                })
            self.astar.diagonal_movement = True

        # 2. 스무딩 레벨 변경
        if len(alternatives) < max_alternatives:
            smooth_route = await self.find_route(
                db, map_id, start, end,
                {'use_cache': False, 'smoothing_level': 'high'}
            )
            if smooth_route.get('success') and smooth_route['polyline'] != main_route['polyline']:
                alternatives.append({
                    'type': 'smooth',
                    'description': '부드러운 경로',
                    **smooth_route
                })

        # 대체 경로 정렬 (거리 기준)
        alternatives.sort(key=lambda x: x.get('distance_meters', float('inf')))

        return {
            'success': True,
            'map_id': map_id,
            'start': start,
            'end': end,
            'main_route': alternatives[0] if alternatives else None,
            'alternatives': alternatives[1:] if len(alternatives) > 1 else [],
            'total_alternatives': len(alternatives) - 1,
            'processing_time': time.time() - start_time
        }

    async def _get_map_data(self, db: AsyncSession, map_id: str) -> Optional[Map]:
        """지도 데이터 조회"""
        result = await db.execute(select(Map).where(Map.id == map_id))
        return result.scalar_one_or_none()

    async def _get_preprocessed_data(self, db: AsyncSession, map_id: str) -> Optional[PreprocessedMapData]:
        """전처리된 데이터 조회"""
        result = await db.execute(
            select(PreprocessedMapData).where(PreprocessedMapData.map_id == map_id)
        )
        return result.scalar_one_or_none()

    async def _load_grid_data(self, preprocessed_data: PreprocessedMapData) -> Optional[np.ndarray]:
        """그리드 데이터 로드"""
        try:
            if preprocessed_data.walkable_grid:
                # DB에서 직접 로드
                return np.array(preprocessed_data.walkable_grid)

            # 파일에서 로드 (Phase 1 호환성)
            grid_path = self.storage_path / "processed" / preprocessed_data.map_id / "grid.json"
            if grid_path.exists():
                with open(grid_path, 'r') as f:
                    grid_data = json.load(f)
                    return np.array(grid_data)

            return None
        except Exception as e:
            logger.error(f"그리드 데이터 로드 실패: {e}")
            return None

    async def _save_pathfinding_request(self, db: AsyncSession, result: Dict[str, Any]):
        """길찾기 요청 결과를 데이터베이스에 저장"""
        try:
            request = PathfindingRequest(
                id=result.get('path_id'),
                map_id=result['map_id'],
                start_x=result['start'][0],
                start_y=result['start'][1],
                end_x=result['end'][0],
                end_y=result['end'][1],
                result_path=result.get('polyline'),
                svg_path=result.get('svg_path'),
                distance_pixels=result.get('distance_pixels'),
                distance_meters=result.get('distance_meters'),
                processing_time=result.get('processing_time'),
                is_cached=result.get('cached', False)
            )
            db.add(request)
            await db.commit()
        except Exception as e:
            logger.error(f"길찾기 요청 저장 실패: {e}")

    def _generate_cache_key(self, map_id: str, start: Tuple[float, float],
                           end: Tuple[float, float], options: Dict) -> str:
        """캐시 키 생성"""
        key_data = f"{map_id}:{start}:{end}:{sorted(options.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _calculate_difficulty(self, optimized: Dict, distance: float) -> str:
        """경로 난이도 계산"""
        turn_count = len(optimized.get('waypoints', [])) - 2

        if distance < 100 and turn_count < 5:
            return PathDifficulty.EASY.value
        elif distance < 500 and turn_count < 15:
            return PathDifficulty.MODERATE.value
        else:
            return PathDifficulty.HARD.value

    def _calculate_accessibility_score(self, optimized: Dict) -> float:
        """접근성 점수 계산 (0-1)"""
        # 간단한 휴리스틱 기반 점수
        waypoint_count = len(optimized.get('waypoints', []))
        reduction_rate = optimized.get('optimization_stats', {}).get('reduction_rate', 0)

        # 웨이포인트가 적고 경로가 간단할수록 높은 점수
        score = 1.0 - (waypoint_count / 100) * 0.5 - (1 - reduction_rate) * 0.5
        return max(0.0, min(1.0, score))

    async def _optimize_waypoint_order(self, db: AsyncSession, map_id: str,
                                      points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        TSP(Traveling Salesman Problem) 근사 알고리즘으로 경유지 순서 최적화
        간단한 그리디 알고리즘 사용
        """
        if len(points) <= 3:
            return points

        optimized = [points[0]]  # 시작점
        remaining = points[1:]

        while remaining:
            current = optimized[-1]
            # 가장 가까운 점 찾기
            nearest = min(remaining, key=lambda p: self._euclidean_distance(current, p))
            optimized.append(nearest)
            remaining.remove(nearest)

        return optimized

    def _euclidean_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """유클리드 거리 계산"""
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5