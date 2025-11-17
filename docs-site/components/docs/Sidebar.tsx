'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BookOpen, Rocket, Code, FileCode } from 'lucide-react';

interface NavItem {
  title: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  items?: NavItem[];
}

const navigation: NavItem[] = [
  {
    title: '시작하기',
    href: '/docs/getting-started',
    icon: Rocket,
  },
  {
    title: 'API 레퍼런스',
    href: '/docs/api-reference',
    icon: BookOpen,
    items: [
      { title: '지도 업로드', href: '/docs/api-reference/upload' },
      { title: '지도 조회', href: '/docs/api-reference/maps' },
      { title: '경로 찾기', href: '/docs/api-reference/pathfinding' },
    ],
  },
  {
    title: '코드 예제',
    href: '/docs/examples',
    icon: Code,
    items: [
      { title: 'JavaScript', href: '/docs/examples/javascript' },
      { title: 'Python', href: '/docs/examples/python' },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/docs') return pathname === '/docs';
    return pathname?.startsWith(href);
  };

  return (
    <aside className="w-64 flex-shrink-0 border-r border-gray-200 bg-gray-50/50 h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto">
      <nav className="p-6 space-y-8">
        {/* Docs Home */}
        <div>
          <Link
            href="/docs"
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
              pathname === '/docs'
                ? 'bg-primary-100 text-primary-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <FileCode className="w-5 h-5" />
            문서 홈
          </Link>
        </div>

        {/* Navigation Sections */}
        {navigation.map((section) => {
          const Icon = section.icon;
          const sectionActive = isActive(section.href);

          return (
            <div key={section.href}>
              {/* Section Title */}
              <Link
                href={section.href}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg mb-2 transition-colors ${
                  sectionActive && !section.items
                    ? 'bg-primary-100 text-primary-700 font-semibold'
                    : 'text-gray-900 hover:bg-gray-100 font-semibold'
                }`}
              >
                {Icon && <Icon className="w-5 h-5" />}
                {section.title}
              </Link>

              {/* Sub Items */}
              {section.items && (
                <ul className="ml-7 space-y-1">
                  {section.items.map((item) => (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        className={`block px-3 py-1.5 rounded-lg text-sm transition-colors ${
                          isActive(item.href)
                            ? 'text-primary-700 bg-primary-50 font-medium'
                            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                        }`}
                      >
                        {item.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
