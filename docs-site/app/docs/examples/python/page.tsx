import CodeBlock from '@/components/docs/CodeBlock';

export default function PythonExamplesPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">Python 예제</h1>
      <p className="text-xl text-gray-600 mb-8">
        Requests 라이브러리를 사용한 Python 스크립트 예제입니다.
      </p>

      {/* Complete Example */}
      <h2 id="complete-example" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        전체 예제
      </h2>
      <p>지도 업로드부터 경로 찾기까지 전체 프로세스를 구현한 예제입니다.</p>

      <CodeBlock
        language="python"
        title="pathfinding_client.py"
        code={`import requests
import time
from typing import Dict, List, Tuple

class PathfindingClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}

    def upload_map(self, file_path: str, name: str, map_type: str) -> Dict:
        """지도 이미지 업로드"""
        url = f"{self.base_url}/api/v1/maps/upload"

        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "name": name,
                "map_type": map_type
            }

            response = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()

    def get_maps(self) -> List[Dict]:
        """지도 목록 조회"""
        url = f"{self.base_url}/api/v1/maps/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_map(self, map_id: int) -> Dict:
        """특정 지도 조회"""
        url = f"{self.base_url}/api/v1/maps/{map_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def find_path(
        self,
        map_id: int,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> Dict:
        """경로 찾기"""
        url = f"{self.base_url}/api/v1/pathfinding/route"

        data = {
            "map_id": map_id,
            "start": {"x": start[0], "y": start[1]},
            "end": {"x": end[0], "y": end[1]}
        }

        response = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json=data
        )
        response.raise_for_status()
        return response.json()

# 사용 예제
def main():
    # 클라이언트 초기화
    client = PathfindingClient(
        base_url="http://localhost:8000",
        api_key="YOUR_API_KEY"
    )

    # 지도 업로드
    print("지도 업로드 중...")
    upload_result = client.upload_map(
        file_path="map.jpg",
        name="My Map",
        map_type="park"
    )
    map_id = upload_result["map"]["id"]
    print(f"지도 ID: {map_id}")

    # 처리 완료 대기
    print("처리 대기 중...")
    time.sleep(5)

    # 경로 찾기
    print("경로 찾기 중...")
    path_result = client.find_path(
        map_id=map_id,
        start=(10, 20),
        end=(100, 200)
    )

    print(f"거리: {path_result['distance']}m")
    print(f"예상 시간: {path_result['estimated_time']}분")
    print(f"경로 포인트 수: {len(path_result['path'])}")

if __name__ == "__main__":
    main()`}
      />

      {/* Simple Example */}
      <h2 id="simple-example" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        간단한 예제
      </h2>
      <p>빠르게 시작할 수 있는 간단한 예제입니다.</p>

      <CodeBlock
        language="python"
        title="simple_example.py"
        code={`import requests

# 설정
API_BASE_URL = "http://localhost:8000"
API_KEY = "YOUR_API_KEY"
headers = {"X-API-Key": API_KEY}

# 1. 지도 업로드
with open("map.jpg", "rb") as f:
    files = {"file": f}
    data = {"name": "Test Map", "map_type": "park"}

    response = requests.post(
        f"{API_BASE_URL}/api/v1/maps/upload",
        headers=headers,
        files=files,
        data=data
    )
    map_id = response.json()["map"]["id"]
    print(f"지도 ID: {map_id}")

# 2. 경로 찾기
path_data = {
    "map_id": map_id,
    "start": {"x": 10, "y": 20},
    "end": {"x": 100, "y": 200}
}

response = requests.post(
    f"{API_BASE_URL}/api/v1/pathfinding/route",
    headers={**headers, "Content-Type": "application/json"},
    json=path_data
)

result = response.json()
print(f"거리: {result['distance']}m")
print(f"경로: {len(result['path'])} 포인트")`}
      />
    </div>
  );
}
