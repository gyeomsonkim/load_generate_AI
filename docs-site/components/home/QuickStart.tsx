import Link from 'next/link';
import { CheckCircle2, ArrowRight } from 'lucide-react';

const steps = [
  {
    number: '01',
    title: 'API 키 발급',
    description: 'Dashboard에서 6자리 API 키를 발급받으세요. 아이디와 비밀번호 없이 키만으로 간편하게 인증할 수 있습니다.',
    action: 'Dashboard 접속',
    href: '/dashboard',
  },
  {
    number: '02',
    title: '지도 이미지 업로드',
    description: '공원, 건물, 캠퍼스 등의 지도 이미지를 업로드하면 AI가 자동으로 전처리하고 보행 가능 영역을 분석합니다.',
    action: '문서 보기',
    href: '/docs/api-reference/upload',
  },
  {
    number: '03',
    title: '경로 찾기 API 호출',
    description: '출발점과 도착점 좌표를 전송하면 A* 알고리즘이 최적의 경로를 찾아 반환합니다.',
    action: 'API 레퍼런스',
    href: '/docs/api-reference/pathfinding',
  },
];

export default function QuickStart() {
  return (
    <section className="py-24 px-4">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            빠른 시작
          </h2>
          <p className="text-xl text-gray-600">
            3단계로 AI 길찾기 API를 바로 사용해보세요
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-8">
          {steps.map((step, index) => (
            <div
              key={index}
              className="group relative bg-white rounded-2xl p-8 md:p-10 shadow-sm hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-primary-200"
              style={{
                animation: 'fadeIn 0.5s ease-out',
                animationDelay: `${index * 0.15}s`,
                animationFillMode: 'both',
              }}
            >
              <div className="flex flex-col md:flex-row gap-8">
                {/* Number */}
                <div className="flex-shrink-0">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-blue-600 text-white rounded-2xl text-2xl font-bold shadow-lg group-hover:scale-110 transition-transform">
                    {step.number}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 space-y-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-primary-600 transition-colors">
                      {step.title}
                    </h3>
                    <p className="text-lg text-gray-600 leading-relaxed">
                      {step.description}
                    </p>
                  </div>

                  {/* Action Link */}
                  <Link
                    href={step.href}
                    className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-semibold group/link"
                  >
                    {step.action}
                    <ArrowRight className="w-4 h-4 group-hover/link:translate-x-1 transition-transform" />
                  </Link>
                </div>

                {/* Check Icon */}
                <div className="hidden md:flex items-center">
                  <CheckCircle2 className="w-8 h-8 text-green-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>

              {/* Connecting Line */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute left-[4.5rem] top-full h-8 w-0.5 bg-gradient-to-b from-primary-300 to-transparent"></div>
              )}
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <Link
            href="/docs/getting-started"
            className="inline-flex items-center gap-2 px-8 py-4 bg-gray-900 text-white rounded-xl font-semibold text-lg hover:bg-gray-800 transition-all hover:scale-105 shadow-lg"
          >
            전체 가이드 보기
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  );
}
