'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';
import { DashboardStats } from '@/types/dashboard';
import StatsCard from '@/components/dashboard/StatsCard';
import UsageChart from '@/components/dashboard/UsageChart';
import {
  Activity,
  Image,
  TrendingUp,
  Clock,
  AlertCircle,
} from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getDashboardStats();
      setStats(data);
    } catch (err) {
      setError('통계를 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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
          onClick={loadStats}
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          API 사용 현황과 통계를 확인하세요
        </p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="총 API 호출"
          value={stats?.usage.total_calls.toLocaleString() || '0'}
          icon={Activity}
          iconColor="text-blue-600"
          iconBgColor="bg-blue-100"
          change={{
            value: `오늘 ${stats?.usage.calls_today || 0}회`,
            positive: true,
          }}
        />
        <StatsCard
          title="이번 주 호출"
          value={stats?.usage.calls_this_week.toLocaleString() || '0'}
          icon={TrendingUp}
          iconColor="text-green-600"
          iconBgColor="bg-green-100"
        />
        <StatsCard
          title="업로드한 이미지"
          value={stats?.recent_uploads.length || '0'}
          icon={Image}
          iconColor="text-purple-600"
          iconBgColor="bg-purple-100"
        />
        <StatsCard
          title="평균 응답 시간"
          value={`${stats?.usage.average_response_time_ms?.toFixed(0) || '0'}ms`}
          icon={Clock}
          iconColor="text-orange-600"
          iconBgColor="bg-orange-100"
        />
      </div>

      {/* 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UsageChart data={stats?.daily_usage || []} type="line" />
        <UsageChart data={stats?.daily_usage || []} type="bar" />
      </div>

      {/* 최근 업로드 */}
      {stats?.recent_uploads && stats.recent_uploads.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            최근 업로드한 이미지
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stats.recent_uploads.slice(0, 6).map((image) => (
              <div
                key={image.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="font-medium text-gray-900">
                    {image.map?.name || `지도 #${image.map_id}`}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(image.upload_timestamp).toLocaleDateString('ko-KR')}
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {image.map?.map_type || 'Unknown'}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 엔드포인트별 사용량 */}
      {stats?.endpoint_usage && stats.endpoint_usage.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            엔드포인트별 사용량
          </h3>
          <div className="space-y-3">
            {stats.endpoint_usage.map((endpoint, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
              >
                <div className="flex-1">
                  <p className="font-mono text-sm text-gray-900">
                    {endpoint.endpoint}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    평균 {endpoint.average_response_time_ms.toFixed(0)}ms
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">
                    {endpoint.count.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500">호출</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
