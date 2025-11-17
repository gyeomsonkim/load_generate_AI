import CodeBlock from '@/components/docs/CodeBlock';
import ApiEndpoint from '@/components/docs/ApiEndpoint';

export default function PathfindingApiPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">경로 찾기 API</h1>
      <p className="text-xl text-gray-600 mb-8">
        A* 알고리즘을 사용하여 출발점과 도착점 사이의 최적 경로를 계산합니다.
      </p>

      <ApiEndpoint
        method="POST"
        path="/api/v1/pathfinding/route"
        description="지도 위에서 출발점부터 도착점까지의 최단 경로를 찾습니다"
      />

      {/* Request Parameters */}
      <h2 id="parameters" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        요청 파라미터
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Request Body</h3>
      <div className="not-prose">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold">필드</th>
              <th className="text-left py-3 px-4 font-semibold">타입</th>
              <th className="text-left py-3 px-4 font-semibold">필수</th>
              <th className="text-left py-3 px-4 font-semibold">설명</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-3 px-4"><code>map_id</code></td>
              <td className="py-3 px-4">integer</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">경로를 찾을 지도의 ID</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>start</code></td>
              <td className="py-3 px-4">object</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">출발점 좌표 (x, y)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>end</code></td>
              <td className="py-3 px-4">object</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">도착점 좌표 (x, y)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>waypoints</code></td>
              <td className="py-3 px-4">array</td>
              <td className="py-3 px-4">-</td>
              <td className="py-3 px-4 text-gray-600">경유지 좌표 배열</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">요청 예제</h3>
      <CodeBlock
        language="json"
        title="Request Body"
        code={`{
  "map_id": 1,
  "start": {
    "x": 10,
    "y": 20
  },
  "end": {
    "x": 100,
    "y": 200
  },
  "waypoints": [
    { "x": 50, "y": 100 }
  ]
}`}
      />

      {/* Response */}
      <h2 id="response" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        응답
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Success Response</h3>
      <CodeBlock
        language="json"
        code={`{
  "map_id": 1,
  "path": [
    { "x": 10, "y": 20 },
    { "x": 15, "y": 25 },
    { "x": 20, "y": 30 },
    ...
    { "x": 100, "y": 200 }
  ],
  "distance": 145.5,
  "estimated_time": 3.2
}`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Response Fields</h3>
      <div className="not-prose">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold">필드</th>
              <th className="text-left py-3 px-4 font-semibold">타입</th>
              <th className="text-left py-3 px-4 font-semibold">설명</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-3 px-4"><code>path</code></td>
              <td className="py-3 px-4">array</td>
              <td className="py-3 px-4 text-gray-600">좌표 배열 (순서대로)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>distance</code></td>
              <td className="py-3 px-4">float</td>
              <td className="py-3 px-4 text-gray-600">총 거리 (미터)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>estimated_time</code></td>
              <td className="py-3 px-4">float</td>
              <td className="py-3 px-4 text-gray-600">예상 소요 시간 (분)</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Code Examples */}
      <h2 id="examples" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        코드 예제
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">JavaScript</h3>
      <CodeBlock
        language="javascript"
        title="경로 찾기"
        code={`const response = await fetch('http://localhost:8000/api/v1/pathfinding/route', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: JSON.stringify({
    map_id: 1,
    start: { x: 10, y: 20 },
    end: { x: 100, y: 200 }
  })
});

const pathData = await response.json();
console.log(\`거리: \${pathData.distance}m\`);
console.log(\`예상 시간: \${pathData.estimated_time}분\`);
console.log(\`경로 포인트 수: \${pathData.path.length}\`);`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Python</h3>
      <CodeBlock
        language="python"
        title="경로 찾기"
        code={`import requests

url = "http://localhost:8000/api/v1/pathfinding/route"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "YOUR_API_KEY"
}

data = {
    "map_id": 1,
    "start": {"x": 10, "y": 20},
    "end": {"x": 100, "y": 200}
}

response = requests.post(url, headers=headers, json=data)
path_data = response.json()

print(f"거리: {path_data['distance']}m")
print(f"예상 시간: {path_data['estimated_time']}분")
print(f"경로 포인트 수: {len(path_data['path'])}")`}
      />
    </div>
  );
}
