'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Map } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname?.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <Map className="w-6 h-6 text-primary-600" />
            <span>AI 길찾기</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/docs"
              className={`text-sm font-medium transition-colors hover:text-primary-600 ${
                isActive('/docs') ? 'text-primary-600' : 'text-gray-600'
              }`}
            >
              문서
            </Link>
            <Link
              href="/dashboard"
              className={`text-sm font-medium transition-colors hover:text-primary-600 ${
                isActive('/dashboard') ? 'text-primary-600' : 'text-gray-600'
              }`}
            >
              Dashboard
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-gray-600 transition-colors hover:text-primary-600"
            >
              GitHub
            </a>
          </nav>

          {/* Mobile Menu Button */}
          <button className="md:hidden p-2">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
