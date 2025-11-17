import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function CTA() {
  return (
    <section className="py-24 px-4 bg-gradient-to-br from-primary-600 via-blue-600 to-purple-700 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-grid-white/10"></div>
      <div className="absolute top-0 left-0 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>

      <div className="container mx-auto max-w-4xl relative z-10">
        <div className="text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-full text-white text-sm font-medium">
            <Sparkles className="w-4 h-4" />
            <span>지금 바로 시작하세요</span>
          </div>

          {/* Heading */}
          <h2 className="text-4xl md:text-5xl font-bold text-white leading-tight">
            AI 길찾기 API로
            <br />
            프로젝트를 시작하세요
          </h2>

          {/* Description */}
          <p className="text-xl text-white/90 max-w-2xl mx-auto">
            6자리 API 키 하나로 강력한 AI 길찾기 기능을 바로 사용할 수 있습니다.
            무료로 시작해보세요.
          </p>

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Link
              href="/docs/getting-started"
              className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-primary-700 rounded-xl font-semibold text-lg hover:bg-gray-50 transition-all hover:scale-105 shadow-xl"
            >
              지금 시작하기
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>

            <Link
              href="/docs/api-reference"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm border-2 border-white/30 text-white rounded-xl font-semibold text-lg hover:bg-white/20 transition-all hover:scale-105"
            >
              API 문서 보기
            </Link>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 pt-8 text-white/90">
            <div className="text-center">
              <div className="text-2xl font-bold">무료</div>
              <div className="text-sm">시작 비용</div>
            </div>
            <div className="w-px h-12 bg-white/30"></div>
            <div className="text-center">
              <div className="text-2xl font-bold">5분</div>
              <div className="text-sm">설정 시간</div>
            </div>
            <div className="w-px h-12 bg-white/30"></div>
            <div className="text-center">
              <div className="text-2xl font-bold">24/7</div>
              <div className="text-sm">기술 지원</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
