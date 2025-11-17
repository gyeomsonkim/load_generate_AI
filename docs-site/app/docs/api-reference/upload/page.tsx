import CodeBlock from '@/components/docs/CodeBlock';
import ApiEndpoint from '@/components/docs/ApiEndpoint';

export default function UploadApiPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">지도 업로드 API</h1>
      <p className="text-xl text-gray-600 mb-8">
        지도 이미지를 업로드하고 AI 기반 자동 전처리를 시작합니다.
      </p>

      <ApiEndpoint
        method="POST"
        path="/api/v1/maps/upload"
        description="지도 이미지 파일과 메타데이터를 함께 전송합니다"
      />

      {/* Request Parameters */}
      <h2 id="parameters" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        요청 파라미터
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Headers</h3>
      <div className="not-prose">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold">이름</th>
              <th className="text-left py-3 px-4 font-semibold">타입</th>
              <th className="text-left py-3 px-4 font-semibold">필수</th>
              <th className="text-left py-3 px-4 font-semibold">설명</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-3 px-4"><code>X-API-Key</code></td>
              <td className="py-3 px-4">string</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">6자리 API 키</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Form Data</h3>
      <div className="not-prose">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold">이름</th>
              <th className="text-left py-3 px-4 font-semibold">타입</th>
              <th className="text-left py-3 px-4 font-semibold">필수</th>
              <th className="text-left py-3 px-4 font-semibold">설명</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-3 px-4"><code>file</code></td>
              <td className="py-3 px-4">File</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">지도 이미지 파일 (JPG, PNG)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>name</code></td>
              <td className="py-3 px-4">string</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">지도 이름</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>description</code></td>
              <td className="py-3 px-4">string</td>
              <td className="py-3 px-4">-</td>
              <td className="py-3 px-4 text-gray-600">지도 설명</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>map_type</code></td>
              <td className="py-3 px-4">string</td>
              <td className="py-3 px-4"><span className="text-red-600">✓</span></td>
              <td className="py-3 px-4 text-gray-600">지도 타입 (park, building, campus, other)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>scale_meters_per_pixel</code></td>
              <td className="py-3 px-4">float</td>
              <td className="py-3 px-4">-</td>
              <td className="py-3 px-4 text-gray-600">픽셀당 미터 비율</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Response */}
      <h2 id="response" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        응답
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Success Response</h3>
      <p>성공 시 다음과 같은 JSON 응답을 반환합니다:</p>

      <CodeBlock
        language="json"
        code={`{
  "id": 1,
  "message": "지도 업로드 성공",
  "map": {
    "id": 1,
    "name": "Central Park",
    "description": "센트럴 파크 지도",
    "map_type": "park",
    "original_filename": "central_park.jpg",
    "file_size": 2048576,
    "image_width": 1920,
    "image_height": 1080,
    "scale_meters_per_pixel": 0.5,
    "processing_status": "pending",
    "created_at": "2024-11-17T12:00:00Z",
    "updated_at": "2024-11-17T12:00:00Z"
  }
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
              <td className="py-3 px-4"><code>processing_status</code></td>
              <td className="py-3 px-4">string</td>
              <td className="py-3 px-4 text-gray-600">pending, processing, completed, failed</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>file_size</code></td>
              <td className="py-3 px-4">integer</td>
              <td className="py-3 px-4 text-gray-600">파일 크기 (bytes)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>image_width</code></td>
              <td className="py-3 px-4">integer</td>
              <td className="py-3 px-4 text-gray-600">이미지 너비 (pixels)</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code>image_height</code></td>
              <td className="py-3 px-4">integer</td>
              <td className="py-3 px-4 text-gray-600">이미지 높이 (pixels)</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Examples */}
      <h2 id="examples" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        코드 예제
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">JavaScript/Fetch</h3>
      <CodeBlock
        language="javascript"
        title="지도 업로드 (JavaScript)"
        code={`const formData = new FormData();
formData.append('file', document.getElementById('mapFile').files[0]);
formData.append('name', 'My Map');
formData.append('description', 'A sample map');
formData.append('map_type', 'park');
formData.append('scale_meters_per_pixel', '0.5');

const response = await fetch('http://localhost:8000/api/v1/maps/upload', {
  method: 'POST',
  headers: {
    'X-API-Key': 'ABC123'
  },
  body: formData
});

const data = await response.json();
console.log('업로드된 지도 ID:', data.map.id);`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">Python/Requests</h3>
      <CodeBlock
        language="python"
        title="지도 업로드 (Python)"
        code={`import requests

url = "http://localhost:8000/api/v1/maps/upload"
headers = {"X-API-Key": "ABC123"}

with open("my_map.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "name": "My Map",
        "description": "A sample map",
        "map_type": "park",
        "scale_meters_per_pixel": 0.5
    }

    response = requests.post(url, headers=headers, files=files, data=data)

result = response.json()
print(f"업로드된 지도 ID: {result['map']['id']}")`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">cURL</h3>
      <CodeBlock
        language="bash"
        title="지도 업로드 (cURL)"
        code={`curl -X POST "http://localhost:8000/api/v1/maps/upload" \\
  -H "X-API-Key: ABC123" \\
  -F "file=@my_map.jpg" \\
  -F "name=My Map" \\
  -F "description=A sample map" \\
  -F "map_type=park" \\
  -F "scale_meters_per_pixel=0.5"`}
      />

      {/* Error Cases */}
      <h2 id="errors" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        에러 케이스
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">401 Unauthorized</h3>
      <p>API 키가 없거나 유효하지 않은 경우:</p>
      <CodeBlock
        language="json"
        code={`{
  "error": "유효하지 않은 API 키입니다",
  "status_code": 401
}`}
      />

      <h3 className="text-2xl font-bold text-gray-900 mt-6 mb-3">400 Bad Request</h3>
      <p>필수 파라미터가 누락되거나 잘못된 경우:</p>
      <CodeBlock
        language="json"
        code={`{
  "error": "필수 파라미터가 누락되었습니다",
  "detail": "name 필드는 필수입니다",
  "status_code": 400
}`}
      />
    </div>
  );
}
