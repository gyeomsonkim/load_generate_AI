"""
이미지 전처리 모듈 - Mock 버전
Python 3.14 호환성 문제로 임시 사용
"""
import json
import time
from typing import Dict, Any, List
from pathlib import Path
import random
import logging

logger = logging.getLogger(__name__)


class MapPreprocessor:
    """지도 이미지 전처리 클래스 (Mock)"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        logger.warning("⚠️ Mock preprocessor 사용 중 - 실제 이미지 처리 없음")

    def preprocess_map(self, image_path: str, output_dir: str) -> Dict[str, Any]:
        """
        지도 이미지를 전처리 (Mock 버전)
        실제 이미지 처리 없이 더미 데이터 생성
        """
        start_time = time.time()

        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 더미 이미지 크기
        width = 1024
        height = 768

        logger.info(f"[Mock] 이미지 크기: {width}x{height}")

        # 더미 그리드 생성 (100x100)
        grid_size = (100, 100)
        grid = [[random.choice([0, 1]) for _ in range(grid_size[1])]
                for _ in range(grid_size[0])]

        # 그리드 저장
        grid_path = output_path / "grid.json"
        with open(grid_path, 'w') as f:
            json.dump(grid, f)

        # 더미 장애물 생성
        obstacles = [
            {
                'id': i,
                'centroid': [random.randint(0, width), random.randint(0, height)],
                'area': random.randint(50, 500),
                'bbox': [0, 0, 100, 100],
                'type': random.choice(['wall', 'building', 'obstacle'])
            }
            for i in range(10)
        ]

        obstacles_path = output_path / "obstacles.json"
        with open(obstacles_path, 'w') as f:
            json.dump(obstacles, f)

        # 더미 입구 지점
        entrance_points = [
            {'position': [0.0, 0.5], 'direction': 'west'},
            {'position': [1.0, 0.5], 'direction': 'east'},
            {'position': [0.5, 0.0], 'direction': 'north'},
            {'position': [0.5, 1.0], 'direction': 'south'},
        ]

        # 처리 시간
        processing_time = time.time() - start_time

        # 결과 반환
        results = {
            'original_size': (width, height),
            'preprocessing_steps': ['mock_processing'],
            'gray_image': str(output_path / "mock_gray.png"),
            'binary_image': str(output_path / "mock_binary.png"),
            'edge_image': str(output_path / "mock_edges.png"),
            'walkable_mask': str(output_path / "mock_walkable.png"),
            'navigation_grid': str(grid_path),
            'grid_size': grid_size,
            'obstacles': obstacles,
            'obstacle_count': len(obstacles),
            'entrance_points': entrance_points,
            'walkable_percentage': random.uniform(60, 80),
            'visualization': str(output_path / "mock_visualization.png"),
            'processing_time': processing_time,
            'is_mock': True  # Mock 데이터임을 표시
        }

        logger.info(f"[Mock] 전처리 완료: {processing_time:.2f}초")
        return results