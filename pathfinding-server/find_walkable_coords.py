"""
통행 가능한 좌표를 찾는 스크립트
"""
import json
import numpy as np
import random

# 가장 최근 맵의 그리드 파일 읽기
map_id = "908b8c76-086d-467c-9f5e-2f8a159ba919"
grid_file = f'storage/processed/{map_id}/grid.json'

with open(grid_file, 'r') as f:
    grid_data = json.load(f)

grid = np.array(grid_data)
height, width = grid.shape
print(f"그리드 크기: {height}x{width}")
print(f"원본 이미지: 816x548 (cell_size=5로 축소)")
print(f"통행 가능 비율: {np.sum(grid == 1) / (height * width) * 100:.1f}%")

# 통행 가능한 모든 좌표 찾기
walkable_points = []
for y in range(height):
    for x in range(width):
        if grid[y, x] == 1:
            walkable_points.append((x, y))

print(f"\n통행 가능한 좌표 수: {len(walkable_points)}개")

# 테스트용 좌표 샘플링
if len(walkable_points) > 0:
    # 랜덤하게 몇 개 선택
    sample_size = min(10, len(walkable_points))
    sample_points = random.sample(walkable_points, sample_size)

    print("\n=== 테스트용 좌표 (그리드 좌표) ===")
    for i, (x, y) in enumerate(sample_points[:5]):
        print(f"Point {i+1}: x={x}, y={y}")

    print("\n=== 정규화된 좌표 (0-1 범위) ===")
    for i, (x, y) in enumerate(sample_points[:5]):
        norm_x = x / width
        norm_y = y / height
        print(f"Point {i+1}: ({norm_x:.3f}, {norm_y:.3f})")

    # 시작점과 끝점 추천
    print("\n=== 추천 테스트 경로 ===")

    # 왼쪽 상단 근처에서 시작점 찾기
    start_candidates = [(x, y) for x, y in walkable_points if x < width/3 and y < height/3]
    if start_candidates:
        start_x, start_y = random.choice(start_candidates)
        start_norm = (start_x / width, start_y / height)
        print(f"시작점: ({start_norm[0]:.3f}, {start_norm[1]:.3f})")

    # 오른쪽 하단 근처에서 끝점 찾기
    end_candidates = [(x, y) for x, y in walkable_points if x > 2*width/3 and y > 2*height/3]
    if end_candidates:
        end_x, end_y = random.choice(end_candidates)
        end_norm = (end_x / width, end_y / height)
        print(f"끝점: ({end_norm[0]:.3f}, {end_norm[1]:.3f})")

    # 중간 지점들 (multi-route 테스트용)
    print("\n=== Multi-route 테스트용 경유지 ===")
    regions = [
        ("왼쪽상단", lambda x, y: x < width/3 and y < height/3),
        ("중앙", lambda x, y: width/3 < x < 2*width/3 and height/3 < y < 2*height/3),
        ("오른쪽하단", lambda x, y: x > 2*width/3 and y > 2*height/3),
    ]

    waypoints = []
    for region_name, filter_func in regions:
        candidates = [(x, y) for x, y in walkable_points if filter_func(x, y)]
        if candidates:
            wx, wy = random.choice(candidates)
            wnorm = (wx / width, wy / height)
            waypoints.append(wnorm)
            print(f"{region_name}: ({wnorm[0]:.3f}, {wnorm[1]:.3f})")

    if len(waypoints) >= 3:
        print(f"\n완전한 경로: {waypoints[0]} → {waypoints[1]} → {waypoints[2]}")