'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import {
  LayoutDashboard,
  Images,
  Key,
  BarChart3,
  LogOut,
  Home,
} from 'lucide-react';

const navigation = [
  { name: '개요', href: '/dashboard', icon: LayoutDashboard },
  { name: '이미지', href: '/dashboard/images', icon: Images },
  { name: 'API 키', href: '/dashboard/keys', icon: Key },
  { name: '사용량 통계', href: '/dashboard/usage', icon: BarChart3 },
];

export default function DashboardSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen sticky top-0">
      {/* 로고 */}
      <div className="p-6 border-b border-gray-200">
        <Link
          href="/"
          className="flex items-center gap-2 text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors"
        >
          <Home className="w-6 h-6" />
          <span>AI 길찾기</span>
        </Link>
      </div>

      {/* 네비게이션 */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-primary-50 text-primary-700 font-semibold'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* 로그아웃 */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-all"
        >
          <LogOut className="w-5 h-5" />
          <span>로그아웃</span>
        </button>
      </div>
    </aside>
  );
}
