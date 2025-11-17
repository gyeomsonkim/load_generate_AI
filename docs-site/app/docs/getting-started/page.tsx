import Link from 'next/link';
import { ArrowRight, Key, Upload, Route } from 'lucide-react';
import CodeBlock from '@/components/docs/CodeBlock';
import ApiEndpoint from '@/components/docs/ApiEndpoint';

export default function GettingStartedPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">시작하기</h1>
      <p className="text-xl text-gray-600 mb-8">
        AI 길찾기 API를 사용하여 첫 번째 경로를 찾아보세요. 5분이면 충분합니다!
      </p>

      {/* Step 1 */}
      <h2 id="step-1" className="text-3xl font-bold text-gray-900 mt-12 mb-4 flex items-center gap-3">
        <div className="flex items-center justify-center w-10 h-10 bg-primary-600 text-white rounded-full font-bold">
          1
        </div>
        API 키 발급
      </h2>
      <p>
        먼저 Dashboard에서 API 키를 발급받아야 합니다. 아이디와 비밀번호 없이
        6자리 키만으로 간편하게 인증할 수 있습니다.
      </p>

      <div className="not-prose my-6 p-6 bg-blue-50 border border-blue-200 rounded-xl">
        <div className="flex items-start gap-3">
          <Key className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h4 className="font-semibold text-blue-900 mb-2">
              API 키 발급 방법
            </h4>
            <ol className="text-sm text-blue-800 space-y-1">
              <li>1. Dashboard 페이지로 이동합니다</li>
              <li>2. &quot;새 API 키 생성&quot; 버튼을 클릭합니다</li>
              <li>3. 6자리 키가 자동으로 생성됩니다</li>
              <li>4. 생성된 키를 안전한 곳에 보관하세요</li>
            </ol>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 mt-3 text-blue-600 hover:text-blue-700 font-medium"
            >
              Dashboard로 이동
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Step 2 */}
      <h2 id="step-2" className="text-3xl font-bold text-gray-900 mt-12 mb-4 flex items-center gap-3">
        <div className="flex items-center justify-center w-10 h-10 bg-primary-600 text-white rounded-full font-bold">
          2
        </div>
        지도 이미지 업로드
      </h2>
      <p>
        API 키를 발급받았다면 이제 지도 이미지를 업로드할 수 있습니다. 공원,
        건물, 캠퍼스 등 다양한 지도를 지원합니다.
      </p>

      <ApiEndpoint
        method="POST"
        path="/api/v1/maps/upload"
        description="지도 이미지를 업로드하고 자동 전처리를 시작합니다"
      />

      <h3 id="upload-javascript" className="text-2xl font-bold text-gray-900 mt-6 mb-3">
        JavaScript 예제
      </h3>

      <CodeBlock
        language="javascript"
        title="지도 업로드"
        code={`const formData = new FormData();
formData.append('file', mapImageFile);
formData.append('name', 'Central Park');
formData.append('description', '센트럴 파크 지도');
formData.append('map_type', 'park');
formData.append('scale_meters_per_pixel', '0.5');

const response = await fetch('http://localhost:8000/api/v1/maps/upload', {
  method: 'POST',
  headers: {
    'X-API-Key': 'YOUR_API_KEY'
  },
  body: formData
});

const data = await response.json();
console.log('지도 ID:', data.map.id);
console.log('처리 상태:', data.map.processing_status);`}
      />

      <h3 id="upload-python" className="text-2xl font-bold text-gray-900 mt-6 mb-3">
        Python 예제
      </h3>

      <CodeBlock
        language="python"
        title="지도 업로드"
        code={`import requests

url = "http://localhost:8000/api/v1/maps/upload"
headers = {"X-API-Key": "YOUR_API_KEY"}

with open("central_park.jpg", "rb") as f:
    files = {"file": f}
    data = {
        "name": "Central Park",
        "description": "센트럴 파크 지도",
        "map_type": "park",
        "scale_meters_per_pixel": 0.5
    }

    response = requests.post(url, headers=headers, files=files, data=data)

map_data = response.json()
print(f"지도 ID: {map_data['map']['id']}")
print(f"처리 상태: {map_data['map']['processing_status']}")`}
      />

      {/* Step 3 */}
      <h2 id="step-3" className="text-3xl font-bold text-gray-900 mt-12 mb-4 flex items-center gap-3">
        <div className="flex items-center justify-center w-10 h-10 bg-primary-600 text-white rounded-full font-bold">
          3
        </div>
        경로 찾기
      </h2>
      <p>
        지도 업로드가 완료되면 이제 경로를 찾을 수 있습니다. 출발점과 도착점
        좌표를 지정하여 최적의 경로를 계산합니다.
      </p>

      <ApiEndpoint
        method="POST"
        path="/api/v1/pathfinding/route"
        description="출발점과 도착점 사이의 최적 경로를 계산합니다"
      />

      <h3 id="pathfinding-javascript" className="text-2xl font-bold text-gray-900 mt-6 mb-3">
        JavaScript 예제
      </h3>

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
console.log('경로:', pathData.path);
console.log('거리:', pathData.distance, 'm');
console.log('예상 시간:', pathData.estimated_time, '분');`}
      />

      <h3 id="pathfinding-python" className="text-2xl font-bold text-gray-900 mt-6 mb-3">
        Python 예제
      </h3>

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

print(f"경로: {path_data['path']}")
print(f"거리: {path_data['distance']} m")
print(f"예상 시간: {path_data['estimated_time']} 분")`}
      />

      {/* Next Steps */}
      <div className="mt-16 p-6 bg-green-50 border border-green-200 rounded-xl not-prose">
        <h3 className="text-xl font-bold text-gray-900 mb-3">
          축하합니다! 🎉
        </h3>
        <p className="text-gray-700 mb-4">
          첫 번째 API 호출을 성공적으로 완료했습니다. 이제 더 많은 기능을
          살펴보세요.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            href="/docs/api-reference"
            className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
          >
            API 레퍼런스 보기
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/docs/examples"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-green-300 text-green-700 rounded-lg font-semibold hover:bg-green-50 transition-colors"
          >
            더 많은 예제 보기
          </Link>
        </div>
      </div>
    </div>
  );
}
