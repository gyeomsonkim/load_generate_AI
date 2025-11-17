import Link from 'next/link';
import { Upload, Map, Route, ArrowRight } from 'lucide-react';

export default function ApiReferencePage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">API 레퍼런스</h1>
      <p className="text-xl text-gray-600 mb-8">
        AI 길찾기 API의 모든 엔드포인트와 파라미터에 대한 상세한 설명입니다.
      </p>

      {/* Base URL */}
      <h2 id="base-url" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        Base URL
      </h2>
      <div className="not-prose my-4">
        <code className="block px-4 py-3 bg-gray-900 text-gray-100 rounded-lg font-mono text-sm">
          http://localhost:8000
        </code>
      </div>
      <p>
        모든 API 요청은 위의 Base URL을 사용합니다. 프로덕션 환경에서는 실제
        도메인으로 변경됩니다.
      </p>

      {/* Authentication */}
      <h2 id="authentication" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        인증
      </h2>
      <p>
        모든 API 요청에는 HTTP 헤더에 API 키가 필요합니다. Dashboard에서 발급받은
        6자리 키를 사용하세요.
      </p>
      <div className="not-prose my-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-sm text-gray-600 mb-2">헤더 형식:</p>
        <code className="block px-4 py-3 bg-gray-900 text-gray-100 rounded-lg font-mono text-sm">
          X-API-Key: YOUR_API_KEY
        </code>
      </div>

      {/* API Endpoints */}
      <h2 id="endpoints" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        API 엔드포인트
      </h2>
      <p>AI 길찾기 API는 다음 3가지 주요 엔드포인트를 제공합니다:</p>

      {/* Endpoint Cards */}
      <div className="grid md:grid-cols-3 gap-6 my-8 not-prose">
        <Link
          href="/docs/api-reference/upload"
          className="group p-6 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">지도 업로드</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            지도 이미지를 업로드하고 자동 전처리를 시작합니다
          </p>
          <div className="flex items-center gap-2 text-primary-600 text-sm font-medium">
            상세 보기 →
          </div>
        </Link>

        <Link
          href="/docs/api-reference/maps"
          className="group p-6 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Map className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">지도 조회</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            업로드한 지도 목록과 상세 정보를 조회합니다
          </p>
          <div className="flex items-center gap-2 text-primary-600 text-sm font-medium">
            상세 보기 →
          </div>
        </Link>

        <Link
          href="/docs/api-reference/pathfinding"
          className="group p-6 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Route className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">경로 찾기</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            출발점과 도착점 사이의 최적 경로를 계산합니다
          </p>
          <div className="flex items-center gap-2 text-primary-600 text-sm font-medium">
            상세 보기 →
          </div>
        </Link>
      </div>

      {/* Error Handling */}
      <h2 id="errors" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        에러 처리
      </h2>
      <p>API는 표준 HTTP 상태 코드를 사용하여 요청의 성공 또는 실패를 나타냅니다.</p>

      <h3 id="status-codes" className="text-2xl font-bold text-gray-900 mt-6 mb-3">
        HTTP 상태 코드
      </h3>
      <div className="not-prose">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b-2 border-gray-300">
              <th className="text-left py-3 px-4 font-semibold">코드</th>
              <th className="text-left py-3 px-4 font-semibold">의미</th>
              <th className="text-left py-3 px-4 font-semibold">설명</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="py-3 px-4"><code className="text-green-600">200</code></td>
              <td className="py-3 px-4">OK</td>
              <td className="py-3 px-4 text-gray-600">요청 성공</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code className="text-green-600">201</code></td>
              <td className="py-3 px-4">Created</td>
              <td className="py-3 px-4 text-gray-600">리소스 생성 성공</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code className="text-yellow-600">400</code></td>
              <td className="py-3 px-4">Bad Request</td>
              <td className="py-3 px-4 text-gray-600">잘못된 요청</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code className="text-red-600">401</code></td>
              <td className="py-3 px-4">Unauthorized</td>
              <td className="py-3 px-4 text-gray-600">인증 실패</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code className="text-red-600">404</code></td>
              <td className="py-3 px-4">Not Found</td>
              <td className="py-3 px-4 text-gray-600">리소스를 찾을 수 없음</td>
            </tr>
            <tr>
              <td className="py-3 px-4"><code className="text-red-600">500</code></td>
              <td className="py-3 px-4">Internal Server Error</td>
              <td className="py-3 px-4 text-gray-600">서버 오류</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3 id="error-response" className="text-2xl font-bold text-gray-900 mt-6 mb-3">
        에러 응답 형식
      </h3>
      <p>에러 발생 시 다음과 같은 JSON 형식으로 응답합니다:</p>
      <div className="not-prose my-4">
        <code className="block px-4 py-3 bg-gray-900 text-gray-100 rounded-lg font-mono text-sm whitespace-pre">
{`{
  "error": "에러 메시지",
  "detail": "상세 설명 (선택사항)",
  "status_code": 400
}`}
        </code>
      </div>

      {/* Rate Limiting */}
      <h2 id="rate-limiting" className="text-3xl font-bold text-gray-900 mt-12 mb-4">
        속도 제한
      </h2>
      <p>API 남용을 방지하기 위해 다음과 같은 속도 제한이 적용됩니다:</p>
      <ul>
        <li><strong>일반 요청</strong>: 분당 100회</li>
        <li><strong>이미지 업로드</strong>: 분당 10회</li>
        <li><strong>경로 찾기</strong>: 분당 50회</li>
      </ul>
      <p>
        속도 제한을 초과하면 <code>429 Too Many Requests</code> 에러가
        반환됩니다.
      </p>

      {/* Next Steps */}
      <div className="mt-16 p-6 bg-blue-50 border border-blue-200 rounded-xl not-prose">
        <h3 className="text-xl font-bold text-gray-900 mb-3">다음 단계</h3>
        <p className="text-gray-700 mb-4">
          각 API 엔드포인트의 상세한 사용법을 확인하세요.
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            href="/docs/api-reference/upload"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            지도 업로드 API
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/docs/examples"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-blue-300 text-blue-700 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            코드 예제 보기
          </Link>
        </div>
      </div>
    </div>
  );
}
