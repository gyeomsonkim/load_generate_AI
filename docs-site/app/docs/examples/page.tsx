import Link from 'next/link';
import { Code2, ArrowRight } from 'lucide-react';

export default function ExamplesPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">코드 예제</h1>
      <p className="text-xl text-gray-600 mb-8">
        JavaScript와 Python으로 작성된 실전 예제를 확인하세요.
      </p>

      {/* Language Cards */}
      <div className="grid md:grid-cols-2 gap-6 my-12 not-prose">
        <Link
          href="/docs/examples/javascript"
          className="group p-8 bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-200 rounded-2xl hover:border-yellow-400 hover:shadow-xl transition-all"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-yellow-400 rounded-xl">
              <Code2 className="w-8 h-8 text-yellow-900" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">JavaScript</h3>
          </div>
          <p className="text-gray-700 mb-4">
            Fetch API를 사용한 브라우저 및 Node.js 환경 예제
          </p>
          <div className="flex items-center gap-2 text-yellow-700 font-semibold">
            예제 보기
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>

        <Link
          href="/docs/examples/python"
          className="group p-8 bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-2xl hover:border-blue-400 hover:shadow-xl transition-all"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-400 rounded-xl">
              <Code2 className="w-8 h-8 text-blue-900" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900">Python</h3>
          </div>
          <p className="text-gray-700 mb-4">
            Requests 라이브러리를 사용한 Python 스크립트 예제
          </p>
          <div className="flex items-center gap-2 text-blue-700 font-semibold">
            예제 보기
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>
      </div>

      {/* Quick Example */}
      <h2 id="quick-example" className="text-3xl font-bold text-gray-900 mt-16 mb-4">
        빠른 예제
      </h2>
      <p>
        다음은 지도 업로드부터 경로 찾기까지의 전체 프로세스를 보여주는 간단한
        예제입니다:
      </p>

      <div className="not-prose my-6 p-6 bg-gray-50 border border-gray-200 rounded-xl">
        <ol className="space-y-4 text-gray-700">
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
              1
            </span>
            <span>API 키를 발급받습니다</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
              2
            </span>
            <span>지도 이미지를 업로드합니다</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
              3
            </span>
            <span>처리 완료를 기다립니다 (자동)</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
              4
            </span>
            <span>경로 찾기 API를 호출합니다</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
              5
            </span>
            <span>반환된 경로를 지도에 표시합니다</span>
          </li>
        </ol>
      </div>

      {/* Use Cases */}
      <h2 id="use-cases" className="text-3xl font-bold text-gray-900 mt-16 mb-4">
        활용 사례
      </h2>

      <h3 className="text-2xl font-bold text-gray-900 mt-8 mb-3">
        실내 네비게이션
      </h3>
      <p>
        쇼핑몰, 공항, 병원 등 실내 공간에서 사용자를 목적지까지 안내하는
        네비게이션 앱을 만들 수 있습니다.
      </p>

      <h3 className="text-2xl font-bold text-gray-900 mt-8 mb-3">
        캠퍼스 가이드
      </h3>
      <p>
        대학교 캠퍼스, 산업 단지 등에서 건물 간 최적 경로를 안내하는 서비스를
        구축할 수 있습니다.
      </p>

      <h3 className="text-2xl font-bold text-gray-900 mt-8 mb-3">
        공원 투어
      </h3>
      <p>
        공원이나 관광지에서 주요 명소를 연결하는 최적의 관람 경로를 추천할 수
        있습니다.
      </p>
    </div>
  );
}
