import Link from 'next/link';
import { Github, Mail } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="font-bold text-lg mb-4">AI 길찾기 API</h3>
            <p className="text-sm text-gray-600">
              지도 이미지 기반 AI 경로 찾기 서비스
            </p>
          </div>

          {/* Documentation */}
          <div>
            <h4 className="font-semibold mb-4">문서</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/docs/getting-started" className="text-gray-600 hover:text-primary-600">
                  시작하기
                </Link>
              </li>
              <li>
                <Link href="/docs/api-reference" className="text-gray-600 hover:text-primary-600">
                  API 레퍼런스
                </Link>
              </li>
              <li>
                <Link href="/docs/examples" className="text-gray-600 hover:text-primary-600">
                  예제
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold mb-4">리소스</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/dashboard" className="text-gray-600 hover:text-primary-600">
                  Dashboard
                </Link>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-primary-600">
                  서비스 상태
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-primary-600">
                  FAQ
                </a>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-semibold mb-4">연락처</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://github.com"
                  className="flex items-center gap-2 text-gray-600 hover:text-primary-600"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="w-4 h-4" />
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="mailto:contact@example.com"
                  className="flex items-center gap-2 text-gray-600 hover:text-primary-600"
                >
                  <Mail className="w-4 h-4" />
                  Email
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t text-center text-sm text-gray-600">
          <p>© 2024 AI Pathfinding API. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
