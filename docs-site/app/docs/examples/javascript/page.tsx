import CodeBlock from '@/components/docs/CodeBlock';

export default function JavaScriptExamplesPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        JavaScript 예제
      </h1>
      <p className="text-xl text-gray-600 mb-8">
        Fetch API를 사용한 브라우저 및 Node.js 환경에서의 사용 예제입니다.
      </p>

      {/* Complete Example */}
      <h2 id="complete-example" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        전체 예제
      </h2>
      <p>지도 업로드부터 경로 찾기까지 전체 프로세스를 구현한 예제입니다.</p>

      <CodeBlock
        language="javascript"
        title="complete-example.js"
        code={`// API 설정
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'YOUR_API_KEY';

// 1. 지도 업로드
async function uploadMap(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('name', 'My Map');
  formData.append('map_type', 'park');

  const response = await fetch(\`\${API_BASE_URL}/api/v1/maps/upload\`, {
    method: 'POST',
    headers: { 'X-API-Key': API_KEY },
    body: formData
  });

  return await response.json();
}

// 2. 지도 목록 조회
async function getMaps() {
  const response = await fetch(\`\${API_BASE_URL}/api/v1/maps/\`, {
    headers: { 'X-API-Key': API_KEY }
  });

  return await response.json();
}

// 3. 경로 찾기
async function findPath(mapId, start, end) {
  const response = await fetch(\`\${API_BASE_URL}/api/v1/pathfinding/route\`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY
    },
    body: JSON.stringify({
      map_id: mapId,
      start,
      end
    })
  });

  return await response.json();
}

// 사용 예제
async function main() {
  try {
    // 지도 업로드
    const fileInput = document.getElementById('mapFile');
    const uploadResult = await uploadMap(fileInput.files[0]);
    console.log('업로드 완료:', uploadResult.map.id);

    // 경로 찾기
    const pathResult = await findPath(
      uploadResult.map.id,
      { x: 10, y: 20 },
      { x: 100, y: 200 }
    );

    console.log('경로:', pathResult.path);
    console.log(\`거리: \${pathResult.distance}m\`);
  } catch (error) {
    console.error('오류 발생:', error);
  }
}

// 실행
main();`}
      />

      {/* React Example */}
      <h2 id="react-example" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        React 예제
      </h2>
      <p>React 애플리케이션에서 AI 길찾기 API를 사용하는 예제입니다.</p>

      <CodeBlock
        language="javascript"
        title="MapUploader.jsx"
        code={`import { useState } from 'react';

function MapUploader() {
  const [mapId, setMapId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [path, setPath] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name);
    formData.append('map_type', 'park');

    try {
      const response = await fetch('http://localhost:8000/api/v1/maps/upload', {
        method: 'POST',
        headers: { 'X-API-Key': 'YOUR_API_KEY' },
        body: formData
      });

      const data = await response.json();
      setMapId(data.map.id);
      console.log('지도 업로드 성공!');
    } catch (error) {
      console.error('업로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFindPath = async () => {
    if (!mapId) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/pathfinding/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'YOUR_API_KEY'
        },
        body: JSON.stringify({
          map_id: mapId,
          start: { x: 10, y: 20 },
          end: { x: 100, y: 200 }
        })
      });

      const data = await response.json();
      setPath(data);
    } catch (error) {
      console.error('경로 찾기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleUpload} accept="image/*" />
      {mapId && (
        <button onClick={handleFindPath} disabled={loading}>
          경로 찾기
        </button>
      )}
      {path && (
        <div>
          <p>거리: {path.distance}m</p>
          <p>예상 시간: {path.estimated_time}분</p>
        </div>
      )}
    </div>
  );
}

export default MapUploader;`}
      />
    </div>
  );
}
