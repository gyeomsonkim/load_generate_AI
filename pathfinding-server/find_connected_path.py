"""
연결된 통행 가능한 경로를 찾는 스크립트
"""
import json
import numpy as np
from scipy import ndimage
import random

# 그리드 파일 읽기
map_id = "908b8c76-086d-467c-9f5e-2f8a159ba919"
grid_file = f'storage/processed/{map_id}/grid.json'

with open(grid_file, 'r') as f:
    grid_data = json.load(f)

grid = np.array(grid_data)
height, width = grid.shape
print(f"그리드 크기: {height}x{width}")
print(f"통행 가능 비율: {np.sum(grid == 1) / (height * width) * 100:.1f}%")

# 연결된 컴포넌트 찾기
labeled_grid, num_components = ndimage.label(grid)
print(f"\n연결된 영역 수: {num_components}개")

# 각 컴포넌트의 크기 계산
component_sizes = []
for i in range(1, num_components + 1):
    size = np.sum(labeled_grid == i)
    component_sizes.append((i, size))

# 크기 순으로 정렬
component_sizes.sort(key=lambda x: x[1], reverse=True)

# 가장 큰 연결 영역 선택
main_component_id = component_sizes[0][0]
main_component_size = component_sizes[0][1]
print(f"가장 큰 연결 영역: ID={main_component_id}, 크기={main_component_size}개 셀")

# 주요 컴포넌트에서만 좌표 선택
main_mask = (labeled_grid == main_component_id)
walkable_points = []
for y in range(height):
    for x in range(width):
        if main_mask[y, x]:
            walkable_points.append((x, y))

print(f"주요 영역의 통행 가능한 좌표: {len(walkable_points)}개")

# 테스트용 좌표 선택
if len(walkable_points) > 100:
    # 영역별로 좌표 선택
    regions = {
        "왼쪽상단": [],
        "왼쪽하단": [],
        "오른쪽상단": [],
        "오른쪽하단": [],
        "중앙": []
    }

    for x, y in walkable_points:
        if x < width/3 and y < height/3:
            regions["왼쪽상단"].append((x, y))
        elif x < width/3 and y > 2*height/3:
            regions["왼쪽하단"].append((x, y))
        elif x > 2*width/3 and y < height/3:
            regions["오른쪽상단"].append((x, y))
        elif x > 2*width/3 and y > 2*height/3:
            regions["오른쪽하단"].append((x, y))
        elif width/3 < x < 2*width/3 and height/3 < y < 2*height/3:
            regions["중앙"].append((x, y))

    print("\n=== 연결된 영역에서 선택한 테스트 좌표 ===")

    # 단일 경로용
    if regions["왼쪽상단"] and regions["오른쪽하단"]:
        start_x, start_y = random.choice(regions["왼쪽상단"])
        end_x, end_y = random.choice(regions["오른쪽하단"])

        print(f"\n단일 경로 테스트:")
        print(f"  시작점: ({start_x/width:.3f}, {start_y/height:.3f}) → grid[{start_y}, {start_x}]")
        print(f"  끝점: ({end_x/width:.3f}, {end_y/height:.3f}) → grid[{end_y}, {end_x}]")

    # 다중 경로용
    print(f"\n다중 경로 테스트:")
    waypoints = []
    for region_name, points in regions.items():
        if points and len(waypoints) < 4:
            wx, wy = random.choice(points)
            waypoints.append((wx/width, wy/height))
            print(f"  {region_name}: ({wx/width:.3f}, {wy/height:.3f}) → grid[{wy}, {wx}]")

    if len(waypoints) >= 4:
        print(f"\n완전한 경로 (4개 지점):")
        for i, (nx, ny) in enumerate(waypoints[:4]):
            print(f"  Point {i+1}: ({nx:.3f}, {ny:.3f})")

    # 대체 경로용
    if regions["왼쪽하단"] and regions["오른쪽상단"]:
        alt_start_x, alt_start_y = random.choice(regions["왼쪽하단"])
        alt_end_x, alt_end_y = random.choice(regions["오른쪽상단"])

        print(f"\n대체 경로 테스트:")
        print(f"  시작점: ({alt_start_x/width:.3f}, {alt_start_y/height:.3f})")
        print(f"  끝점: ({alt_end_x/width:.3f}, {alt_end_y/height:.3f})")

    # 캐시 테스트용 (단일 경로와 동일)
    print(f"\n캐시 테스트 (단일 경로와 동일):")
    if regions["왼쪽상단"] and regions["오른쪽하단"]:
        print(f"  시작점: ({start_x/width:.3f}, {start_y/height:.3f})")
        print(f"  끝점: ({end_x/width:.3f}, {end_y/height:.3f})")