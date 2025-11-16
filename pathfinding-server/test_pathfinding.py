"""
Phase 2 길찾기 API 테스트 스크립트
A* 알고리즘 기반 경로 찾기 기능 테스트
"""
import requests
import json
import time
import random
from pathlib import Path

# 서버 URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# 색상 코드
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message):
    print(f"{RED}❌ {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")


def test_single_route(map_id: str):
    """단일 경로 찾기 테스트"""
    print(f"\n{BOLD}=== 1. 단일 경로 찾기 테스트 ==={RESET}")

    # 연결된 영역 내의 좌표 사용 (find_connected_path.py 결과 기반)
    start = (0.227, 0.284)  # 왼쪽 상단 영역 (연결된 주요 영역)
    end = (0.706, 0.844)    # 오른쪽 하단 영역 (연결된 주요 영역)

    print_info(f"시작점: {start}")
    print_info(f"종료점: {end}")

    payload = {
        "map_id": map_id,
        "start": start,
        "end": end,
        "options": {
            "smoothing_level": "medium"
        }
    }

    response = requests.post(
        f"{API_URL}/pathfinding/route",
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        print_success("경로 찾기 성공!")
        print(f"  📍 경로 ID: {data['path_id']}")
        print(f"  📏 거리: {data['metadata']['distance_meters']:.2f}m")
        print(f"  ⏱️  예상 시간: {data['metadata']['estimated_time_seconds']:.1f}초")
        print(f"  🎯 난이도: {data['metadata']['difficulty']}")
        print(f"  ♿ 접근성 점수: {data['metadata']['accessibility_score']:.2f}")
        print(f"  🔄 회전 수: {data['metadata']['turn_count']}")
        print(f"  💨 처리 시간: {data['processing_time']:.3f}초")
        print(f"  💾 캐시 사용: {'Yes' if data['cached'] else 'No'}")

        # SVG 경로 일부 출력
        if data.get('svg_path'):
            svg_preview = data['svg_path'][:100] + "..." if len(data['svg_path']) > 100 else data['svg_path']
            print(f"  🎨 SVG 경로: {svg_preview}")

        return data
    else:
        print_error(f"경로 찾기 실패: {response.status_code}")
        print(f"  오류: {response.text}")
        return None


def test_multi_route(map_id: str):
    """다중 경로 찾기 테스트"""
    print(f"\n{BOLD}=== 2. 다중 경로 찾기 테스트 ==={RESET}")

    # 연결된 영역 내의 경유지 사용 (순차적 경로)
    points = [
        (0.117, 0.229),  # 시작점 (왼쪽상단)
        (0.227, 0.284),  # 경유지 1 (좌측중앙)
        (0.706, 0.844),  # 경유지 2 (우측하단)
        (0.994, 0.862),  # 종료점 (오른쪽하단)
    ]

    print_info(f"경유 지점: {points}")

    payload = {
        "map_id": map_id,
        "points": points,
        "optimize_order": True,
        "return_to_start": False,
        "options": {}
    }

    response = requests.post(
        f"{API_URL}/pathfinding/multi-route",
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        print_success("다중 경로 찾기 성공!")
        print(f"  📍 경로 ID: {data['path_id']}")
        print(f"  🔢 구간 수: {data['segment_count']}")
        print(f"  📏 총 거리: {data['total_distance_meters']:.2f}m")
        print(f"  ⏱️  총 시간: {data['total_time_seconds']:.1f}초")
        print(f"  💨 처리 시간: {data['processing_time']:.3f}초")

        print("\n  📋 구간별 정보:")
        for seg in data['segments']:
            print(f"    구간 {seg['segment_index'] + 1}: "
                  f"{seg['distance']:.1f}m, {seg['time']:.1f}초")

        return data
    else:
        print_error(f"다중 경로 찾기 실패: {response.status_code}")
        print(f"  오류: {response.text}")
        return None


def test_alternative_routes(map_id: str):
    """대체 경로 찾기 테스트"""
    print(f"\n{BOLD}=== 3. 대체 경로 찾기 테스트 ==={RESET}")

    # 연결된 영역 내의 좌표 사용
    start_x, start_y = 0.049, 0.835  # 왼쪽 하단 (연결된 영역)
    end_x, end_y = 0.669, 0.055      # 오른쪽 상단 (연결된 영역)

    print_info(f"시작점: ({start_x}, {start_y})")
    print_info(f"종료점: ({end_x}, {end_y})")

    response = requests.get(
        f"{API_URL}/pathfinding/alternatives",
        params={
            "map_id": map_id,
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "max_alternatives": 3
        }
    )

    if response.status_code == 200:
        data = response.json()
        print_success("대체 경로 찾기 성공!")

        if data.get('main_route'):
            main = data['main_route']
            print(f"\n  🎯 메인 경로:")
            print(f"    - 타입: {main['type']}")
            print(f"    - 설명: {main['description']}")
            print(f"    - 거리: {main['distance_meters']:.2f}m")
            print(f"    - 시간: {main['estimated_time_seconds']:.1f}초")

        if data.get('alternatives'):
            print(f"\n  🔀 대체 경로 ({len(data['alternatives'])}개):")
            for i, alt in enumerate(data['alternatives'], 1):
                print(f"    대체 경로 {i}:")
                print(f"      - 타입: {alt['type']}")
                print(f"      - 설명: {alt['description']}")
                print(f"      - 거리: {alt['distance_meters']:.2f}m")
                print(f"      - 시간: {alt['estimated_time_seconds']:.1f}초")

        return data
    else:
        print_error(f"대체 경로 찾기 실패: {response.status_code}")
        print(f"  오류: {response.text}")
        return None


def test_pathfinding_history(map_id: str):
    """길찾기 기록 조회 테스트"""
    print(f"\n{BOLD}=== 4. 길찾기 기록 조회 테스트 ==={RESET}")

    response = requests.get(
        f"{API_URL}/pathfinding/history/{map_id}",
        params={"limit": 5}
    )

    if response.status_code == 200:
        data = response.json()
        print_success("기록 조회 성공!")
        print(f"  📊 총 기록 수: {data['total']}")

        if data['history']:
            print("\n  📜 최근 기록:")
            for i, record in enumerate(data['history'], 1):
                print(f"    {i}. ID: {record['id'][:8]}...")
                print(f"       시작: {record['start']}")
                print(f"       종료: {record['end']}")
                if record.get('distance_meters'):
                    print(f"       거리: {record['distance_meters']:.2f}m")
                print(f"       캐시: {'Yes' if record['cached'] else 'No'}")

        return data
    else:
        print_error(f"기록 조회 실패: {response.status_code}")
        return None


def test_cache_performance(map_id: str):
    """캐시 성능 테스트"""
    print(f"\n{BOLD}=== 5. 캐시 성능 테스트 ==={RESET}")

    # 동일한 경로 요청 (연결된 영역 내 좌표)
    start = (0.227, 0.284)  # 왼쪽 상단 영역 (단일 경로와 동일)
    end = (0.706, 0.844)    # 오른쪽 하단 영역 (단일 경로와 동일)

    payload = {
        "map_id": map_id,
        "start": start,
        "end": end,
        "options": {}
    }

    # 첫 번째 요청 (캐시 생성)
    print_info("첫 번째 요청 (캐시 생성)...")
    start_time = time.time()
    response1 = requests.post(f"{API_URL}/pathfinding/route", json=payload)
    time1 = time.time() - start_time

    if response1.status_code == 200:
        data1 = response1.json()
        print(f"  ⏱️  처리 시간: {time1:.3f}초")
        print(f"  💾 캐시 사용: {'Yes' if data1['cached'] else 'No'}")

    # 두 번째 요청 (캐시 사용)
    print_info("\n두 번째 요청 (캐시 사용)...")
    start_time = time.time()
    response2 = requests.post(f"{API_URL}/pathfinding/route", json=payload)
    time2 = time.time() - start_time

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"  ⏱️  처리 시간: {time2:.3f}초")
        print(f"  💾 캐시 사용: {'Yes' if data2['cached'] else 'No'}")

        # 성능 향상 계산
        if time1 > 0:
            improvement = (time1 - time2) / time1 * 100
            print_success(f"\n캐시 성능 향상: {improvement:.1f}%")
            print(f"  🚀 속도 향상: {time1/time2:.1f}배 빨라짐")


def test_error_handling(map_id: str):
    """에러 처리 테스트"""
    print(f"\n{BOLD}=== 6. 에러 처리 테스트 ==={RESET}")

    # 잘못된 좌표 테스트
    print_info("잘못된 좌표 테스트...")
    payload = {
        "map_id": map_id,
        "start": (1.5, 0.5),  # 범위 초과
        "end": (0.5, 0.5),
        "options": {}
    }

    response = requests.post(f"{API_URL}/pathfinding/route", json=payload)
    if response.status_code == 400:
        print_success("잘못된 좌표 감지 성공")
    else:
        print_error("잘못된 좌표 감지 실패")

    # 존재하지 않는 지도 테스트
    print_info("\n존재하지 않는 지도 테스트...")
    payload = {
        "map_id": "non-existent-map-id",
        "start": (0.1, 0.1),
        "end": (0.9, 0.9),
        "options": {}
    }

    response = requests.post(f"{API_URL}/pathfinding/route", json=payload)
    if response.status_code in [404, 500]:
        print_success("존재하지 않는 지도 에러 처리 성공")
    else:
        print_error("존재하지 않는 지도 에러 처리 실패")


def run_all_tests(map_id: str = None):
    """모든 테스트 실행"""
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}🚀 Phase 2 길찾기 API 테스트 시작{RESET}")
    print(f"{BOLD}{'='*50}{RESET}")

    # map_id가 제공되지 않은 경우, 먼저 지도 목록 확인
    if not map_id:
        print_info("지도 목록 확인 중...")
        response = requests.get(f"{API_URL}/maps/")
        if response.status_code == 200:
            maps = response.json()
            if maps and len(maps) > 0:
                map_id = maps[0]['id']
                print_success(f"테스트할 지도 선택: {maps[0]['name']} (ID: {map_id[:8]}...)")
            else:
                print_error("업로드된 지도가 없습니다. 먼저 지도를 업로드하세요.")
                return
        else:
            print_error("지도 목록을 가져올 수 없습니다.")
            return

    # 테스트 실행
    test_results = []

    # 1. 단일 경로 테스트
    result = test_single_route(map_id)
    test_results.append(("단일 경로", result is not None))

    time.sleep(1)

    # 2. 다중 경로 테스트
    result = test_multi_route(map_id)
    test_results.append(("다중 경로", result is not None))

    time.sleep(1)

    # 3. 대체 경로 테스트
    result = test_alternative_routes(map_id)
    test_results.append(("대체 경로", result is not None))

    time.sleep(1)

    # 4. 기록 조회 테스트
    result = test_pathfinding_history(map_id)
    test_results.append(("기록 조회", result is not None))

    # 5. 캐시 성능 테스트
    test_cache_performance(map_id)
    test_results.append(("캐시 성능", True))

    # 6. 에러 처리 테스트
    test_error_handling(map_id)
    test_results.append(("에러 처리", True))

    # 결과 요약
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}📊 테스트 결과 요약{RESET}")
    print(f"{BOLD}{'='*50}{RESET}")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        if result:
            print(f"  {GREEN}✅ {test_name}: PASSED{RESET}")
        else:
            print(f"  {RED}❌ {test_name}: FAILED{RESET}")

    print(f"\n{BOLD}총 결과: {passed}/{total} 테스트 통과{RESET}")

    if passed == total:
        print(f"\n{GREEN}{BOLD}🎉 모든 테스트 성공!{RESET}")
    else:
        print(f"\n{YELLOW}{BOLD}⚠️ 일부 테스트 실패{RESET}")


if __name__ == "__main__":
    print(f"{BLUE}서버 주소: {BASE_URL}{RESET}")
    print(f"{BLUE}API 문서: {BASE_URL}/docs{RESET}")

    try:
        # 서버 상태 확인
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print_success("서버 연결 성공!")
            run_all_tests("908b8c76-086d-467c-9f5e-2f8a159ba919")
        else:
            print_error("서버 상태가 정상이 아닙니다.")
    except requests.exceptions.ConnectionError:
        print_error("서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print_info(f"실행 명령: cd pathfinding-server && python -m app.main")
    except Exception as e:
        print_error(f"예상치 못한 오류: {e}")