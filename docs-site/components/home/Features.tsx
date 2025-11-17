import { Upload, Brain, Zap, Shield, BarChart3, Code } from 'lucide-react';

const features = [
  {
    icon: Upload,
    title: '간편한 지도 업로드',
    description: 'JPG, PNG 등 다양한 형식의 지도 이미지를 업로드하고 자동으로 전처리합니다.',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    icon: Brain,
    title: 'AI 자동 분석',
    description: 'OpenCV 기반 이미지 처리로 보행 가능 영역과 장애물을 자동으로 감지합니다.',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  {
    icon: Zap,
    title: 'A* 경로 찾기',
    description: 'A* 알고리즘으로 최단 거리, 다중 경유지, 대체 경로를 빠르게 계산합니다.',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
  },
  {
    icon: Shield,
    title: '간단한 인증',
    description: '6자리 API 키만으로 간편하게 인증하고 서비스를 이용할 수 있습니다.',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
  {
    icon: BarChart3,
    title: '실시간 통계',
    description: 'API 사용량, 처리 시간, 성공률 등을 실시간으로 모니터링할 수 있습니다.',
    color: 'text-pink-600',
    bgColor: 'bg-pink-50',
  },
  {
    icon: Code,
    title: '다양한 언어 지원',
    description: 'JavaScript, Python 등 다양한 언어로 작성된 코드 예제를 제공합니다.',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
  },
];

export default function Features() {
  return (
    <section className="py-24 px-4 bg-gray-50">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            강력한 기능
          </h2>
          <p className="text-xl text-gray-600">
            AI 길찾기 API가 제공하는 핵심 기능들을 살펴보세요
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="group bg-white rounded-2xl p-8 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border border-gray-100"
                style={{
                  animation: 'fadeIn 0.5s ease-out',
                  animationDelay: `${index * 0.1}s`,
                  animationFillMode: 'both',
                }}
              >
                {/* Icon */}
                <div className={`inline-flex p-4 rounded-xl ${feature.bgColor} mb-6 group-hover:scale-110 transition-transform`}>
                  <Icon className={`w-8 h-8 ${feature.color}`} />
                </div>

                {/* Title */}
                <h3 className="text-xl font-bold text-gray-900 mb-3">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
