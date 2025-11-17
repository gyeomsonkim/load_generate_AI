import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI 길찾기 API - 문서',
  description: '지도 이미지 기반 AI 경로 찾기 API 서비스',
  keywords: ['AI', '길찾기', 'pathfinding', 'API', '지도', 'navigation'],
  authors: [{ name: 'AI Pathfinding Team' }],
  openGraph: {
    title: 'AI 길찾기 API',
    description: '지도 이미지 기반 AI 경로 찾기 API 서비스',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
