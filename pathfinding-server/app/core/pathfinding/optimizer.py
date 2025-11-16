"""
경로 최적화 모듈
A* 알고리즘으로 찾은 경로를 더 부드럽고 효율적으로 최적화
"""
import math
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from scipy import interpolate
import logging

logger = logging.getLogger(__name__)


class PathOptimizer:
    """
    경로 최적화 클래스
    찾은 경로를 더 자연스럽고 효율적으로 만듦
    """

    def __init__(self):
        self.min_segment_length = 5  # 최소 세그먼트 길이 (픽셀)
        self.smoothing_factor = 0.5  # 스무딩 강도 (0-1)
        self.angle_threshold = 30  # 각도 임계값 (도)

    def optimize_path(self, path: List[Tuple[float, float]],
                      options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        경로를 최적화하여 여러 형식으로 반환

        Args:
            path: 원본 경로 (정규화된 좌표)
            options: 최적화 옵션

        Returns:
            최적화된 경로 정보 딕셔너리
        """
        if not path or len(path) < 2:
            return {
                'original_path': path,
                'optimized_path': path,
                'smooth_path': path,
                'waypoints': path,
                'svg_path': '',
                'distance': 0
            }

        options = options or {}

        # 1. 중복 점 제거
        unique_path = self._remove_duplicates(path)

        # 2. 웨이포인트 감소
        reduced_path = self.reduce_waypoints(unique_path)

        # 3. 경로 스무딩
        smooth_path = self.smooth_path(reduced_path, options.get('smoothing_level', 'medium'))

        # 4. SVG 경로 생성
        svg_path = self.create_svg_path(smooth_path)

        # 5. 거리 계산
        distance = self.calculate_distance(smooth_path)

        return {
            'original_path': path,
            'optimized_path': reduced_path,
            'smooth_path': smooth_path,
            'waypoints': self._extract_key_waypoints(reduced_path),
            'svg_path': svg_path,
            'distance': distance,
            'optimization_stats': {
                'original_points': len(path),
                'optimized_points': len(reduced_path),
                'smooth_points': len(smooth_path),
                'reduction_rate': 1 - (len(reduced_path) / len(path)) if path else 0
            }
        }

    def smooth_path(self, path: List[Tuple[float, float]],
                    smoothing_level: str = 'medium') -> List[Tuple[float, float]]:
        """
        경로를 부드럽게 만들기 (베지어 곡선 또는 스플라인 보간)

        Args:
            path: 원본 경로
            smoothing_level: 스무딩 수준 ('none', 'low', 'medium', 'high')

        Returns:
            스무싱된 경로
        """
        if len(path) < 3:
            return path

        # 스무딩 수준에 따른 파라미터 설정
        smoothing_params = {
            'none': 0,
            'low': 10,
            'medium': 20,
            'high': 30
        }
        num_points = smoothing_params.get(smoothing_level, 20)

        if num_points == 0:
            return path

        try:
            # 경로를 x, y 좌표로 분리
            x_coords = [p[0] for p in path]
            y_coords = [p[1] for p in path]

            # 스플라인 보간 생성
            if len(path) >= 4:
                # Cubic spline for smooth curves
                tck, u = interpolate.splprep([x_coords, y_coords], s=0, k=min(3, len(path)-1))
                u_new = np.linspace(0, 1, num_points * len(path))
                smooth_coords = interpolate.splev(u_new, tck)

                smooth_path = list(zip(smooth_coords[0], smooth_coords[1]))
            else:
                # Linear interpolation for few points
                t = np.linspace(0, 1, len(path))
                t_new = np.linspace(0, 1, num_points * len(path))

                f_x = interpolate.interp1d(t, x_coords, kind='linear')
                f_y = interpolate.interp1d(t, y_coords, kind='linear')

                smooth_path = list(zip(f_x(t_new), f_y(t_new)))

            # 중복 제거
            return self._remove_duplicates(smooth_path)

        except Exception as e:
            logger.warning(f"경로 스무딩 실패: {e}")
            return path

    def reduce_waypoints(self, path: List[Tuple[float, float]],
                        tolerance: float = 0.001) -> List[Tuple[float, float]]:
        """
        Ramer-Douglas-Peucker 알고리즘을 사용한 웨이포인트 감소

        Args:
            path: 원본 경로
            tolerance: 허용 오차

        Returns:
            감소된 웨이포인트 경로
        """
        if len(path) <= 2:
            return path

        # 첫 점과 끝 점 사이의 직선에서 가장 먼 점 찾기
        first = path[0]
        last = path[-1]

        max_dist = 0
        max_idx = 0

        for i in range(1, len(path) - 1):
            dist = self._point_to_line_distance(path[i], first, last)
            if dist > max_dist:
                max_dist = dist
                max_idx = i

        # 임계값보다 거리가 크면 재귀적으로 분할
        if max_dist > tolerance:
            # 왼쪽 부분 처리
            left_path = self.reduce_waypoints(path[:max_idx + 1], tolerance)
            # 오른쪽 부분 처리
            right_path = self.reduce_waypoints(path[max_idx:], tolerance)
            # 결합 (중복 점 제거)
            return left_path[:-1] + right_path
        else:
            # 시작점과 끝점만 유지
            return [first, last]

    def apply_constraints(self, path: List[Tuple[float, float]],
                         constraints: Dict[str, Any]) -> List[Tuple[float, float]]:
        """
        경로에 제약 조건 적용

        Args:
            path: 원본 경로
            constraints: 제약 조건 (예: 특정 영역 회피, 최대 회전 각도 등)

        Returns:
            제약 조건이 적용된 경로
        """
        constrained_path = path.copy()

        # 최대 회전 각도 제약
        if 'max_turn_angle' in constraints:
            max_angle = constraints['max_turn_angle']
            constrained_path = self._apply_turn_angle_constraint(constrained_path, max_angle)

        # 금지 구역 회피
        if 'avoid_areas' in constraints:
            avoid_areas = constraints['avoid_areas']
            constrained_path = self._avoid_areas(constrained_path, avoid_areas)

        # 선호 경로 따라가기
        if 'prefer_path' in constraints:
            prefer_path = constraints['prefer_path']
            constrained_path = self._follow_preferred_path(constrained_path, prefer_path)

        return constrained_path

    def create_svg_path(self, path: List[Tuple[float, float]]) -> str:
        """
        경로를 SVG path 문자열로 변환

        Args:
            path: 경로 좌표 리스트

        Returns:
            SVG path 문자열
        """
        if not path:
            return ""

        # SVG 명령어 생성
        svg_commands = []

        # 시작점으로 이동
        svg_commands.append(f"M {path[0][0]:.4f},{path[0][1]:.4f}")

        if len(path) > 2:
            # 베지어 곡선으로 부드러운 경로 생성
            for i in range(1, len(path) - 1, 2):
                if i + 1 < len(path):
                    # Quadratic Bezier curve
                    control = path[i]
                    end = path[i + 1]
                    svg_commands.append(f"Q {control[0]:.4f},{control[1]:.4f} {end[0]:.4f},{end[1]:.4f}")
                else:
                    # 마지막 점은 직선으로
                    svg_commands.append(f"L {path[i][0]:.4f},{path[i][1]:.4f}")

            # 마지막 점이 처리되지 않았다면 추가
            if len(path) % 2 == 0:
                svg_commands.append(f"L {path[-1][0]:.4f},{path[-1][1]:.4f}")
        else:
            # 점이 2개만 있으면 직선
            svg_commands.append(f"L {path[1][0]:.4f},{path[1][1]:.4f}")

        return " ".join(svg_commands)

    def calculate_distance(self, path: List[Tuple[float, float]]) -> float:
        """
        경로의 총 거리 계산 (정규화된 좌표 기준)

        Args:
            path: 경로 좌표 리스트

        Returns:
            총 거리
        """
        if len(path) < 2:
            return 0

        total_distance = 0
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i + 1]
            distance = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
            total_distance += distance

        return total_distance

    def _remove_duplicates(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """중복 점 제거"""
        if not path:
            return path

        unique_path = [path[0]]
        for i in range(1, len(path)):
            if path[i] != path[i - 1]:
                unique_path.append(path[i])

        return unique_path

    def _extract_key_waypoints(self, path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        주요 웨이포인트 추출 (방향이 크게 바뀌는 지점)
        """
        if len(path) <= 2:
            return path

        waypoints = [path[0]]

        for i in range(1, len(path) - 1):
            angle = self._calculate_angle(path[i - 1], path[i], path[i + 1])
            # 30도 이상 방향이 바뀌면 웨이포인트로 추가
            if abs(angle) > math.radians(self.angle_threshold):
                waypoints.append(path[i])

        waypoints.append(path[-1])
        return waypoints

    def _point_to_line_distance(self, point: Tuple[float, float],
                                line_start: Tuple[float, float],
                                line_end: Tuple[float, float]) -> float:
        """점에서 직선까지의 수직 거리 계산"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end

        # 직선의 길이
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if line_length == 0:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        # 점에서 직선까지의 거리
        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / (line_length ** 2)))
        projection_x = x1 + t * (x2 - x1)
        projection_y = y1 + t * (y2 - y1)

        return math.sqrt((x0 - projection_x) ** 2 + (y0 - projection_y) ** 2)

    def _calculate_angle(self, p1: Tuple[float, float],
                        p2: Tuple[float, float],
                        p3: Tuple[float, float]) -> float:
        """세 점 사이의 각도 계산"""
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])

        # 벡터 정규화
        len_v1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        len_v2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if len_v1 == 0 or len_v2 == 0:
            return 0

        # 코사인 각도 계산
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        cos_angle = dot_product / (len_v1 * len_v2)
        cos_angle = max(-1, min(1, cos_angle))  # 수치 오차 보정

        return math.acos(cos_angle)

    def _apply_turn_angle_constraint(self, path: List[Tuple[float, float]],
                                    max_angle: float) -> List[Tuple[float, float]]:
        """최대 회전 각도 제약 적용"""
        # TODO: 구현 필요 (복잡한 로직)
        return path

    def _avoid_areas(self, path: List[Tuple[float, float]],
                    avoid_areas: List[Dict]) -> List[Tuple[float, float]]:
        """금지 구역 회피"""
        # TODO: 구현 필요 (복잡한 로직)
        return path

    def _follow_preferred_path(self, path: List[Tuple[float, float]],
                              preferred_path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """선호 경로 따라가기"""
        # TODO: 구현 필요 (복잡한 로직)
        return path