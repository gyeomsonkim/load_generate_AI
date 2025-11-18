'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/auth';
import { apiClient } from '@/lib/api/client';
import { Loader2, Key } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const [digits, setDigits] = useState<string[]>(['', '', '', '', '', '']);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleDigitChange = (index: number, value: string) => {
    // 숫자만 입력 가능
    if (value && !/^\d$/.test(value)) return;

    const newDigits = [...digits];
    newDigits[index] = value;
    setDigits(newDigits);
    setError('');

    // 자동으로 다음 입력칸으로 이동
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // 모든 자리가 채워지면 자동 로그인 시도
    if (newDigits.every((d) => d !== '') && index === 5) {
      handleLogin(newDigits.join(''));
    }
  };

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    // Backspace 처리
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData('text').replace(/\D/g, '');
    if (pasteData.length === 6) {
      const newDigits = pasteData.split('');
      setDigits(newDigits);
      inputRefs.current[5]?.focus();
      handleLogin(pasteData);
    }
  };

  const handleLogin = async (apiKey: string) => {
    setLoading(true);
    setError('');

    try {
      // API 키 검증
      await apiClient.verifyApiKey(apiKey);

      // 로그인 성공
      apiClient.setApiKey(apiKey);
      login(apiKey);

      // 대시보드로 이동
      router.push('/dashboard');
    } catch (err) {
      setError('유효하지 않은 API 키입니다. 다시 확인해주세요.');
      setDigits(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const apiKey = digits.join('');
    if (apiKey.length === 6) {
      handleLogin(apiKey);
    } else {
      setError('6자리 API 키를 모두 입력해주세요.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-blue-50 to-purple-50 relative overflow-hidden">
      {/* 배경 장식 */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-200/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* 로그인 카드 */}
      <div className="w-full max-w-md px-6">
        <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-100">
          {/* 헤더 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-2xl mb-4">
              <Key className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Dashboard 로그인
            </h1>
            <p className="text-gray-600">
              6자리 API 키를 입력해주세요
            </p>
          </div>

          {/* 로그인 폼 */}
          <form onSubmit={handleSubmit}>
            {/* 6자리 입력 */}
            <div className="flex gap-3 justify-center mb-6">
              {digits.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => {
                    inputRefs.current[index] = el;
                  }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleDigitChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={index === 0 ? handlePaste : undefined}
                  disabled={loading}
                  className={`w-14 h-16 text-center text-2xl font-bold border-2 rounded-xl transition-all ${
                    error
                      ? 'border-red-300 bg-red-50'
                      : digit
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } focus:outline-none focus:ring-4 focus:ring-primary-100 disabled:bg-gray-50 disabled:cursor-not-allowed`}
                />
              ))}
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600 text-center">
                {error}
              </div>
            )}

            {/* 로그인 버튼 */}
            <button
              type="submit"
              disabled={loading || digits.some((d) => d === '')}
              className="w-full py-4 bg-gradient-to-r from-primary-600 to-blue-600 text-white font-semibold rounded-xl hover:from-primary-700 hover:to-blue-700 focus:outline-none focus:ring-4 focus:ring-primary-100 transition-all disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>확인 중...</span>
                </>
              ) : (
                '로그인'
              )}
            </button>
          </form>

          {/* 도움말 */}
          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-sm text-gray-500 text-center">
              API 키가 없으신가요?{' '}
              <a
                href="/docs/getting-started"
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                시작하기 가이드
              </a>
              에서 발급 방법을 확인하세요.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
