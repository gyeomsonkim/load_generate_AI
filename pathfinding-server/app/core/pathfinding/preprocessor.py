"""
이미지 전처리 모듈 - Phase 1의 핵심
지도 이미지를 길찾기 알고리즘에 사용할 수 있도록 전처리
"""
import cv2
import numpy as np
from typing import Tuple, Dict, List, Optional, Any
import json
from pathlib import Path
import logging
from skimage import morphology, measure
from scipy import ndimage
import time

logger = logging.getLogger(__name__)


class MapPreprocessor:
    """지도 이미지 전처리 클래스"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_walkway_width = self.config.get('min_walkway_width', 10)
        self.obstacle_threshold = self.config.get('obstacle_threshold', 200)
        self.edge_threshold_low = self.config.get('edge_threshold_low', 50)
        self.edge_threshold_high = self.config.get('edge_threshold_high', 150)

    def preprocess_map(self, image_path: str, output_dir: str) -> Dict[str, Any]:
        """
        지도 이미지를 전처리하여 길찾기에 사용할 수 있도록 변환

        Returns:
            전처리 결과 딕셔너리
        """
        start_time = time.time()

        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")

        height, width = image.shape[:2]
        logger.info(f"이미지 크기: {width}x{height}")

        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {
            'original_size': (width, height),
            'preprocessing_steps': []
        }

        # 1. 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_path = output_path / "gray.png"
        cv2.imwrite(str(gray_path), gray)
        results['gray_image'] = str(gray_path)
        results['preprocessing_steps'].append('grayscale_conversion')

        # 2. 노이즈 제거 (가우시안 블러)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 3. 이진화 처리 (적응형 임계값)
        binary = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        binary_path = output_path / "binary.png"
        cv2.imwrite(str(binary_path), binary)
        results['binary_image'] = str(binary_path)
        results['preprocessing_steps'].append('binary_thresholding')

        # 4. 엣지 검출 (Canny)
        edges = cv2.Canny(blurred, self.edge_threshold_low, self.edge_threshold_high)
        edges_path = output_path / "edges.png"
        cv2.imwrite(str(edges_path), edges)
        results['edge_image'] = str(edges_path)
        results['preprocessing_steps'].append('edge_detection')

        # 5. 보행 가능 영역 추출
        walkable_mask = self._extract_walkable_areas(binary, edges)
        walkable_path = output_path / "walkable.png"
        cv2.imwrite(str(walkable_path), walkable_mask * 255)
        results['walkable_mask'] = str(walkable_path)
        results['preprocessing_steps'].append('walkable_area_extraction')

        # 6. 그리드 생성 (길찾기용)
        grid = self._create_navigation_grid(walkable_mask)
        grid_path = output_path / "grid.json"
        with open(grid_path, 'w') as f:
            json.dump(grid.tolist(), f)
        results['navigation_grid'] = str(grid_path)
        results['grid_size'] = grid.shape
        results['preprocessing_steps'].append('grid_generation')

        # 7. 장애물 검출
        obstacles = self._detect_obstacles(binary, walkable_mask)
        obstacles_path = output_path / "obstacles.json"
        with open(obstacles_path, 'w') as f:
            json.dump(obstacles, f)
        results['obstacles'] = obstacles
        results['obstacle_count'] = len(obstacles)
        results['preprocessing_steps'].append('obstacle_detection')

        # 8. 입구/출구 지점 감지
        entrance_points = self._detect_entrance_points(walkable_mask, edges)
        results['entrance_points'] = entrance_points
        results['preprocessing_steps'].append('entrance_detection')

        # 9. 보행 가능 영역 비율 계산
        walkable_percentage = np.sum(walkable_mask) / (width * height) * 100
        results['walkable_percentage'] = walkable_percentage

        # 10. 시각화 이미지 생성
        visualization = self._create_visualization(image, walkable_mask, obstacles, entrance_points)
        vis_path = output_path / "visualization.png"
        cv2.imwrite(str(vis_path), visualization)
        results['visualization'] = str(vis_path)

        # 처리 시간
        processing_time = time.time() - start_time
        results['processing_time'] = processing_time

        logger.info(f"전처리 완료: {processing_time:.2f}초")
        return results

    def _extract_walkable_areas(self, binary: np.ndarray, edges: np.ndarray) -> np.ndarray:
        """보행 가능 영역 추출"""
        # 이진 이미지에서 밝은 영역을 보행 가능 영역으로 간주
        walkable = binary > self.obstacle_threshold

        # 엣지 정보를 이용해 경계 보정
        walkable[edges > 0] = 0

        # 모폴로지 연산으로 노이즈 제거
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        walkable = cv2.morphologyEx(walkable.astype(np.uint8), cv2.MORPH_OPEN, kernel)
        walkable = cv2.morphologyEx(walkable, cv2.MORPH_CLOSE, kernel)

        # 작은 구멍 채우기
        walkable = ndimage.binary_fill_holes(walkable)

        # 최소 크기 이하 영역 제거
        walkable = morphology.remove_small_objects(walkable, min_size=100)

        return walkable.astype(np.uint8)

    def _create_navigation_grid(self, walkable_mask: np.ndarray, cell_size: int = 5) -> np.ndarray:
        """
        네비게이션 그리드 생성
        더 낮은 해상도의 그리드로 변환하여 길찾기 성능 향상
        """
        height, width = walkable_mask.shape
        grid_height = height // cell_size
        grid_width = width // cell_size

        grid = np.zeros((grid_height, grid_width), dtype=np.uint8)

        for i in range(grid_height):
            for j in range(grid_width):
                cell = walkable_mask[
                    i * cell_size:(i + 1) * cell_size,
                    j * cell_size:(j + 1) * cell_size
                ]
                # 셀의 70% 이상이 보행 가능하면 그리드 셀을 보행 가능으로 설정
                if np.mean(cell) > 0.7:
                    grid[i, j] = 1

        return grid

    def _detect_obstacles(self, binary: np.ndarray, walkable_mask: np.ndarray) -> List[Dict]:
        """장애물 검출"""
        # 보행 불가능 영역을 장애물로 간주
        obstacle_mask = 1 - walkable_mask

        # 연결된 구성 요소 찾기
        labeled_obstacles = measure.label(obstacle_mask, connectivity=2)
        regions = measure.regionprops(labeled_obstacles)

        obstacles = []
        for region in regions:
            if region.area < 50:  # 너무 작은 영역 무시
                continue

            obstacle = {
                'id': len(obstacles),
                'centroid': [float(region.centroid[1]), float(region.centroid[0])],  # x, y
                'area': int(region.area),
                'bbox': region.bbox,  # minr, minc, maxr, maxc
                'type': self._classify_obstacle(region, binary)
            }
            obstacles.append(obstacle)

        return obstacles

    def _classify_obstacle(self, region, binary: np.ndarray) -> str:
        """장애물 유형 분류 (간단한 휴리스틱 사용)"""
        # 실제로는 ML 모델을 사용하여 분류할 수 있음
        aspect_ratio = region.major_axis_length / (region.minor_axis_length + 0.001)

        if aspect_ratio > 5:
            return "wall"
        elif region.area > 1000:
            return "building"
        else:
            return "obstacle"

    def _detect_entrance_points(self, walkable_mask: np.ndarray, edges: np.ndarray) -> List[Dict]:
        """입구/출구 지점 감지"""
        height, width = walkable_mask.shape
        entrance_points = []

        # 이미지 경계에서 보행 가능한 영역 찾기
        # 상단 경계
        for x in range(0, width, 10):
            if walkable_mask[0, x] == 1:
                entrance_points.append({
                    'position': [x / width, 0],
                    'direction': 'north'
                })

        # 하단 경계
        for x in range(0, width, 10):
            if walkable_mask[height-1, x] == 1:
                entrance_points.append({
                    'position': [x / width, 1.0],
                    'direction': 'south'
                })

        # 좌측 경계
        for y in range(0, height, 10):
            if walkable_mask[y, 0] == 1:
                entrance_points.append({
                    'position': [0, y / height],
                    'direction': 'west'
                })

        # 우측 경계
        for y in range(0, height, 10):
            if walkable_mask[y, width-1] == 1:
                entrance_points.append({
                    'position': [1.0, y / height],
                    'direction': 'east'
                })

        return entrance_points

    def _create_visualization(self, original: np.ndarray, walkable: np.ndarray,
                            obstacles: List[Dict], entrances: List[Dict]) -> np.ndarray:
        """시각화 이미지 생성"""
        vis = original.copy()

        # 보행 가능 영역을 녹색으로 오버레이
        green_overlay = np.zeros_like(vis)
        green_overlay[:, :, 1] = walkable * 100
        vis = cv2.addWeighted(vis, 0.7, green_overlay, 0.3, 0)

        # 장애물 표시
        for obstacle in obstacles[:20]:  # 최대 20개만 표시
            centroid = obstacle['centroid']
            cv2.circle(vis, (int(centroid[0]), int(centroid[1])), 5, (0, 0, 255), -1)

        # 입구 표시
        height, width = original.shape[:2]
        for entrance in entrances:
            pos = entrance['position']
            x, y = int(pos[0] * width), int(pos[1] * height)
            cv2.circle(vis, (x, y), 8, (255, 255, 0), -1)

        return vis