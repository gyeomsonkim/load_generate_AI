import Link from 'next/link';
import { Rocket, BookOpen, Code, ArrowRight } from 'lucide-react';

export default function DocsPage() {
  return (
    <div className="prose prose-gray max-w-none">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        AI 길찾기 API 문서
      </h1>
      <p className="text-xl text-gray-600 mb-8">
        지도 이미지 기반 AI 경로 찾기 API를 사용하여 프로젝트를 시작하세요.
      </p>

      {/* Quick Links */}
      <div className="grid md:grid-cols-3 gap-6 my-12 not-prose">
        <Link
          href="/docs/getting-started"
          className="group p-6 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Rocket className="w-6 h-6 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">시작하기</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            API 키 발급부터 첫 API 호출까지 단계별 가이드
          </p>
          <div className="flex items-center gap-2 text-primary-600 text-sm font-medium">
            빠른 시작 →
          </div>
        </Link>

        <Link
          href="/docs/api-reference"
          className="group p-6 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <BookOpen className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              API 레퍼런스
            </h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            모든 API 엔드포인트와 파라미터 상세 설명
          </p>
          <div className="flex items-center gap-2 text-primary-600 text-sm font-medium">
            문서 보기 →
          </div>
        </Link>

        <Link
          href="/docs/examples"
          className="group p-6 bg-white border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg transition-all"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Code className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">코드 예제</h3>
          </div>
          <p className="text-gray-600 text-sm mb-3">
            JavaScript와 Python으로 작성된 실전 예제
          </p>
          <div className="flex items-center gap-2 text-primary-600 text-sm font-medium">
            예제 보기 →
          </div>
        </Link>
      </div>

      {/* Overview */}
      <h2 id="overview" className="text-3xl font-bold text-gray-900 mt-16 mb-4">
        개요
      </h2>
      <p>
        AI 길찾기 API는 지도 이미지를 업로드하고 AI가 자동으로 보행 가능 영역을
        분석하여 최적의 경로를 찾아주는 서비스입니다. OpenCV 기반 이미지 전처리와
        A* 알고리즘을 활용하여 빠르고 정확한 경로를 제공합니다.
      </p>

      <h3 id="key-features" className="text-2xl font-bold text-gray-900 mt-8 mb-3">
        주요 기능
      </h3>
      <ul className="space-y-2">
        <li>
          <strong>자동 지도 전처리</strong> - 업로드한 이미지를 자동으로 분석하고
          보행 가능 영역을 감지합니다
        </li>
        <li>
          <strong>A* 경로 찾기</strong> - 최단 거리, 다중 경유지, 대체 경로를
          계산합니다
        </li>
        <li>
          <strong>간편한 인증</strong> - 6자리 API 키만으로 쉽게 인증할 수
          있습니다
        </li>
        <li>
          <strong>실시간 통계</strong> - API 사용량과 처리 결과를 Dashboard에서
          확인할 수 있습니다
        </li>
      </ul>

      <h3 id="how-it-works" className="text-2xl font-bold text-gray-900 mt-8 mb-3">
        작동 원리
      </h3>
      <ol className="space-y-2">
        <li>
          <strong>이미지 업로드</strong> - 지도 이미지를 API에 업로드합니다
        </li>
        <li>
          <strong>자동 전처리</strong> - 그레이스케일, 이진화, 엣지 검출 등의
          과정을 거쳐 보행 가능 영역을 추출합니다
        </li>
        <li>
          <strong>그리드 생성</strong> - 길찾기에 최적화된 저해상도 그리드를
          생성합니다
        </li>
        <li>
          <strong>경로 계산</strong> - A* 알고리즘으로 출발점에서 도착점까지의
          최적 경로를 계산합니다
        </li>
      </ol>

      <h2 id="getting-help" className="text-3xl font-bold text-gray-900 mt-16 mb-4">
        도움말
      </h2>
      <p>
        API 사용 중 문제가 발생하거나 질문이 있으시면 다음 채널을 이용해 주세요:
      </p>
      <ul className="space-y-2">
        <li>
          <strong>GitHub Issues</strong> - 버그 리포트나 기능 제안
        </li>
        <li>
          <strong>Email</strong> - contact@example.com
        </li>
        <li>
          <strong>Dashboard</strong> - API 사용량 및 상태 확인
        </li>
      </ul>

      {/* Next Steps */}
      <div className="mt-16 p-6 bg-primary-50 border border-primary-200 rounded-xl not-prose">
        <h3 className="text-xl font-bold text-gray-900 mb-3">다음 단계</h3>
        <p className="text-gray-700 mb-4">
          이제 API를 사용할 준비가 되었습니다. 시작하기 가이드를 따라해보세요!
        </p>
        <Link
          href="/docs/getting-started"
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition-colors"
        >
          시작하기
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
