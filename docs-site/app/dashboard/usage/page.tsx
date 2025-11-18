'use client';

import { useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/lib/api/client';
import { DailyUsage } from '@/types/dashboard';
import UsageChart from '@/components/dashboard/UsageChart';
import { BarChart3, AlertCircle, TrendingUp, Activity } from 'lucide-react';

type Period = 'day' | 'week' | 'month';

export default function UsagePage() {
  const [period, setPeriod] = useState<Period>('week');
  const [usage, setUsage] = useState<DailyUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadUsage = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.getApiUsage(period);
      setUsage(data);
    } catch (err) {
      setError('사용량 데이터를 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    loadUsage();
  }, [loadUsage]);

  const totalCalls = usage.reduce((sum, item) => sum + item.count, 0);
  const averageCalls = usage.length > 0 ? Math.round(totalCalls / usage.length) : 0;
  const maxCalls = Math.max(...usage.map((item) => item.count), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-gray-600">{error}</p>
        <button
          onClick={loadUsage}
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          다시 시도
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">사용량 통계</h1>
          <p className="text-gray-600 mt-2">
            API 호출 횟수와 사용 패턴을 분석하세요
          </p>
        </div>

        {/* 기간 선택 */}
        <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg p-1">
          {(['day', 'week', 'month'] as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                period === p
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {p === 'day' ? '오늘' : p === 'week' ? '이번 주' : '이번 달'}
            </button>
          ))}
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-sm font-medium text-gray-600">총 호출</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {totalCalls.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-sm font-medium text-gray-600">평균 호출</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {averageCalls.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BarChart3 className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-sm font-medium text-gray-600">최대 호출</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {maxCalls.toLocaleString()}
          </p>
        </div>
      </div>

      {/* 차트 */}
      {usage.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 bg-white rounded-xl border border-gray-200">
          <BarChart3 className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-gray-600 text-lg">사용량 데이터가 없습니다</p>
          <p className="text-gray-500 text-sm mt-2">
            API를 호출하면 통계가 표시됩니다
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <UsageChart data={usage} type="line" />
          <UsageChart data={usage} type="bar" />
        </div>
      )}

      {/* 분석 */}
      {usage.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            사용 패턴 분석
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-600">총 호출 수</span>
              <span className="font-semibold text-gray-900">
                {totalCalls.toLocaleString()}회
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-600">일평균 호출 수</span>
              <span className="font-semibold text-gray-900">
                {averageCalls.toLocaleString()}회
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-600">최대 일일 호출 수</span>
              <span className="font-semibold text-gray-900">
                {maxCalls.toLocaleString()}회
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-gray-600">분석 기간</span>
              <span className="font-semibold text-gray-900">
                {period === 'day'
                  ? '오늘'
                  : period === 'week'
                  ? '최근 7일'
                  : '최근 30일'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
