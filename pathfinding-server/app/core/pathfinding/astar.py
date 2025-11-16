"""
A* (A-Star) 길찾기 알고리즘 구현
최단 경로를 찾기 위한 휴리스틱 기반 탐색 알고리즘
"""
import heapq
import math
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class Point:
    """2D 좌표 포인트"""
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, t: Tuple[int, int]) -> 'Point':
        return cls(t[0], t[1])


@dataclass
class Node:
    """A* 알고리즘용 노드"""
    point: Point
    g_cost: float  # 시작점에서 현재 노드까지의 실제 비용
    h_cost: float  # 현재 노드에서 목표점까지의 휴리스틱 비용
    parent: Optional['Node'] = None

    @property
    def f_cost(self) -> float:
        """F = G + H (전체 비용)"""
        return self.g_cost + self.h_cost

    def __lt__(self, other):
        return self.f_cost < other.f_cost


class AStarPathfinder:
    """
    A* 알고리즘을 사용한 길찾기 클래스
    """

    def __init__(self, diagonal_movement: bool = True, smooth_path: bool = True):
        """
        Args:
            diagonal_movement: 대각선 이동 허용 여부
            smooth_path: 경로 스무딩 적용 여부
        """
        self.diagonal_movement = diagonal_movement
        self.smooth_path = smooth_path
        self.directions = self._get_directions()

    def _get_directions(self) -> List[Tuple[int, int, float]]:
        """
        이동 가능한 방향 정의
        Returns: (dx, dy, cost) 튜플 리스트
        """
        # 상하좌우 (비용: 1.0)
        directions = [
            (0, -1, 1.0),   # 위
            (0, 1, 1.0),    # 아래
            (-1, 0, 1.0),   # 왼쪽
            (1, 0, 1.0),    # 오른쪽
        ]

        # 대각선 이동 (비용: 약 1.414)
        if self.diagonal_movement:
            diagonal_cost = math.sqrt(2)
            directions.extend([
                (-1, -1, diagonal_cost),  # 왼쪽 위
                (1, -1, diagonal_cost),   # 오른쪽 위
                (-1, 1, diagonal_cost),   # 왼쪽 아래
                (1, 1, diagonal_cost),    # 오른쪽 아래
            ])

        return directions

    def find_path(self, grid: np.ndarray, start: Tuple[float, float],
                  end: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        """
        A* 알고리즘으로 최단 경로 찾기

        Args:
            grid: 2D 그리드 (0: 장애물, 1: 통행 가능)
            start: 시작 좌표 (정규화된 0-1 범위)
            end: 종료 좌표 (정규화된 0-1 범위)

        Returns:
            경로 좌표 리스트 (정규화된 좌표) 또는 None
        """
        # 정규화된 좌표를 그리드 좌표로 변환
        height, width = grid.shape
        start_point = Point(
            int(start[0] * width),
            int(start[1] * height)
        )
        end_point = Point(
            int(end[0] * width),
            int(end[1] * height)
        )

        # 시작점과 끝점이 유효한지 확인
        if not self._is_valid_point(grid, start_point):
            logger.error(f"시작점이 유효하지 않습니다: {start_point}")
            return None

        if not self._is_valid_point(grid, end_point):
            logger.error(f"종료점이 유효하지 않습니다: {end_point}")
            return None

        # A* 알고리즘 실행
        path = self._astar_search(grid, start_point, end_point)

        if path is None:
            logger.warning(f"경로를 찾을 수 없습니다: {start_point} -> {end_point}")
            return None

        # 경로 스무딩 적용
        if self.smooth_path and len(path) > 2:
            path = self._smooth_path(grid, path)

        # 그리드 좌표를 정규화된 좌표로 변환
        normalized_path = [
            (p.x / width, p.y / height) for p in path
        ]

        return normalized_path

    def _astar_search(self, grid: np.ndarray, start: Point, end: Point) -> Optional[List[Point]]:
        """
        A* 탐색 알고리즘 핵심 구현
        """
        # 열린 집합 (탐색할 노드들) - 최소 힙 사용
        open_set = []
        # 닫힌 집합 (이미 탐색한 노드들)
        closed_set: Set[Point] = set()
        # 각 점에 대한 최소 비용 저장
        g_costs: Dict[Point, float] = {}
        # 부모 노드 저장 (경로 재구성용)
        came_from: Dict[Point, Point] = {}

        # 시작 노드 생성
        start_node = Node(
            point=start,
            g_cost=0,
            h_cost=self._calculate_heuristic(start, end)
        )
        heapq.heappush(open_set, start_node)
        g_costs[start] = 0

        while open_set:
            # F 비용이 가장 낮은 노드 선택
            current_node = heapq.heappop(open_set)
            current = current_node.point

            # 목표 도달 확인
            if current == end:
                return self._reconstruct_path(came_from, current)

            # 이미 처리한 노드는 건너뛰기
            if current in closed_set:
                continue

            closed_set.add(current)

            # 이웃 노드 탐색
            for neighbor, move_cost in self._get_neighbors(grid, current):
                if neighbor in closed_set:
                    continue

                # G 비용 계산
                tentative_g_cost = g_costs[current] + move_cost

                # 더 나은 경로를 찾았거나 처음 방문하는 경우
                if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                    g_costs[neighbor] = tentative_g_cost
                    came_from[neighbor] = current

                    # 이웃 노드를 열린 집합에 추가
                    neighbor_node = Node(
                        point=neighbor,
                        g_cost=tentative_g_cost,
                        h_cost=self._calculate_heuristic(neighbor, end)
                    )
                    heapq.heappush(open_set, neighbor_node)

        # 경로를 찾지 못함
        return None

    def _get_neighbors(self, grid: np.ndarray, point: Point) -> List[Tuple[Point, float]]:
        """
        현재 점에서 이동 가능한 이웃 노드들을 반환
        """
        neighbors = []
        height, width = grid.shape

        for dx, dy, cost in self.directions:
            new_x = point.x + dx
            new_y = point.y + dy
            new_point = Point(new_x, new_y)

            # 유효성 검사
            if not self._is_valid_point(grid, new_point):
                continue

            # 대각선 이동 시 벽 모서리 통과 방지
            if self.diagonal_movement and dx != 0 and dy != 0:
                # 대각선 이동을 위해서는 인접한 두 칸도 통행 가능해야 함
                if not (self._is_walkable(grid, Point(point.x + dx, point.y)) and
                        self._is_walkable(grid, Point(point.x, point.y + dy))):
                    continue

            neighbors.append((new_point, cost))

        return neighbors

    def _is_valid_point(self, grid: np.ndarray, point: Point) -> bool:
        """점이 그리드 내에 있고 통행 가능한지 확인"""
        height, width = grid.shape
        if 0 <= point.x < width and 0 <= point.y < height:
            return grid[point.y, point.x] == 1
        return False

    def _is_walkable(self, grid: np.ndarray, point: Point) -> bool:
        """점이 통행 가능한지 확인"""
        height, width = grid.shape
        if 0 <= point.x < width and 0 <= point.y < height:
            return grid[point.y, point.x] == 1
        return False

    def _calculate_heuristic(self, point1: Point, point2: Point) -> float:
        """
        휴리스틱 함수 (예상 비용)
        여러 휴리스틱 중 선택 가능
        """
        # 유클리드 거리 (대각선 이동 허용 시)
        if self.diagonal_movement:
            return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

        # 맨해튼 거리 (상하좌우만 이동 시)
        return abs(point1.x - point2.x) + abs(point1.y - point2.y)

    def _reconstruct_path(self, came_from: Dict[Point, Point], current: Point) -> List[Point]:
        """
        부모 노드 정보를 사용하여 경로 재구성
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _smooth_path(self, grid: np.ndarray, path: List[Point]) -> List[Point]:
        """
        경로 스무딩 - 불필요한 웨이포인트 제거
        직선으로 연결 가능한 점들을 직접 연결
        """
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current_idx = 0

        while current_idx < len(path) - 1:
            # 현재 위치에서 가능한 한 멀리 있는 점까지 직선으로 연결
            farthest_visible = current_idx + 1

            for i in range(current_idx + 2, len(path)):
                if self._has_line_of_sight(grid, path[current_idx], path[i]):
                    farthest_visible = i
                else:
                    break

            smoothed.append(path[farthest_visible])
            current_idx = farthest_visible

        return smoothed

    def _has_line_of_sight(self, grid: np.ndarray, point1: Point, point2: Point) -> bool:
        """
        두 점 사이에 장애물이 없는지 확인 (Bresenham's line algorithm)
        """
        x1, y1 = point1.x, point1.y
        x2, y2 = point2.x, point2.y

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            # 현재 위치가 통행 불가능하면 시야가 차단됨
            if not self._is_walkable(grid, Point(x1, y1)):
                return False

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return True