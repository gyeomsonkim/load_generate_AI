import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative overflow-hidden pt-20 pb-32 px-4">
      {/* Background decoration */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary-200/30 rounded-full blur-3xl"></div>
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-blue-300/20 rounded-full blur-3xl"></div>
      </div>

      <div className="container mx-auto max-w-6xl">
        <div className="text-center max-w-4xl mx-auto space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 border border-primary-200 rounded-full text-primary-700 text-sm font-medium animate-fade-in">
            <Sparkles className="w-4 h-4" />
            <span>AI 기반 경로 찾기 API</span>
          </div>

          {/* Heading */}
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 leading-tight animate-fade-in">
            지도 이미지를
            <br />
            <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
              스마트한 경로로
            </span>
          </h1>

          {/* Description */}
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto animate-fade-in" style={{ animationDelay: '0.1s' }}>
            OpenCV와 A* 알고리즘을 활용한 AI 길찾기 서비스.
            <br />
            지도 이미지만 업로드하면 자동으로 최적 경로를 찾아드립니다.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <Link
              href="/docs"
              className="group inline-flex items-center gap-2 px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold text-lg hover:bg-primary-700 transition-all hover:scale-105 shadow-lg hover:shadow-xl"
            >
              시작하기
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>

            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white border-2 border-gray-300 text-gray-700 rounded-xl font-semibold text-lg hover:border-gray-400 transition-all hover:scale-105"
            >
              Dashboard 보기
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto pt-12 animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-primary-600">99%</div>
              <div className="text-sm text-gray-600 mt-1">정확도</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-primary-600">&lt;500ms</div>
              <div className="text-sm text-gray-600 mt-1">응답 시간</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-bold text-primary-600">24/7</div>
              <div className="text-sm text-gray-600 mt-1">서비스</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
