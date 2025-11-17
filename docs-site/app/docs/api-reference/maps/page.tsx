import CodeBlock from '@/components/docs/CodeBlock';
import ApiEndpoint from '@/components/docs/ApiEndpoint';

export default function MapsApiPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">지도 조회 API</h1>
      <p className="text-xl text-gray-600 mb-8">
        업로드한 지도의 목록을 조회하거나 특정 지도의 상세 정보를 확인합니다.
      </p>

      {/* Get All Maps */}
      <h2 id="list-maps" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        지도 목록 조회
      </h2>

      <ApiEndpoint
        method="GET"
        path="/api/v1/maps/"
        description="업로드한 모든 지도의 목록을 조회합니다"
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">요청 예제</h3>
      <CodeBlock
        language="javascript"
        code={`const response = await fetch('http://localhost:8000/api/v1/maps/', {
  headers: {
    'X-API-Key': 'YOUR_API_KEY'
  }
});

const maps = await response.json();
console.log('지도 목록:', maps);`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">응답 예제</h3>
      <CodeBlock
        language="json"
        code={`[
  {
    "id": 1,
    "name": "Central Park",
    "map_type": "park",
    "processing_status": "completed",
    "created_at": "2024-11-17T12:00:00Z"
  },
  {
    "id": 2,
    "name": "Building Map",
    "map_type": "building",
    "processing_status": "pending",
    "created_at": "2024-11-17T13:00:00Z"
  }
]`}
      />

      {/* Get Single Map */}
      <h2 id="get-map" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        특정 지도 조회
      </h2>

      <ApiEndpoint
        method="GET"
        path="/api/v1/maps/{map_id}"
        description="특정 지도의 상세 정보를 조회합니다"
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Path Parameters</h3>
      <div className="not-prose">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold">이름</th>
              <th className="text-left py-3 px-4 font-semibold">타입</th>
              <th className="text-left py-3 px-4 font-semibold">설명</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-3 px-4"><code>map_id</code></td>
              <td className="py-3 px-4">integer</td>
              <td className="py-3 px-4 text-gray-600">조회할 지도의 ID</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">요청 예제</h3>
      <CodeBlock
        language="javascript"
        code={`const mapId = 1;
const response = await fetch(\`http://localhost:8000/api/v1/maps/\${mapId}\`, {
  headers: {
    'X-API-Key': 'YOUR_API_KEY'
  }
});

const map = await response.json();
console.log('지도 정보:', map);`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">응답 예제</h3>
      <CodeBlock
        language="json"
        code={`{
  "id": 1,
  "name": "Central Park",
  "description": "센트럴 파크 지도",
  "map_type": "park",
  "original_filename": "central_park.jpg",
  "file_size": 2048576,
  "image_width": 1920,
  "image_height": 1080,
  "scale_meters_per_pixel": 0.5,
  "processing_status": "completed",
  "created_at": "2024-11-17T12:00:00Z",
  "updated_at": "2024-11-17T12:05:00Z",
  "original_image_url": "/media/maps/1/original.jpg",
  "processed_image_url": "/media/maps/1/processed.jpg",
  "grid_data": {...},
  "walkable_areas": [...],
  "obstacles": [...]
}`}
      />
    </div>
  );
}
