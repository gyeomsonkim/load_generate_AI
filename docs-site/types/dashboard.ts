// Dashboard 관련 타입 정의

import { MapInfo } from './api';

/**
 * API 사용 기록
 */
export interface ApiUsageRecord {
  id: number;
  api_key_id: number;
  endpoint: string;
  method: string;
  status_code: number;
  response_time_ms: number;
  timestamp: string;
  request_data?: Record<string, unknown>;
  user_agent?: string;
}

/**
 * 사용자 이미지 정보
 */
export interface UserImage {
  id: number;
  api_key_id: number;
  map_id: number;
  upload_timestamp: string;
  is_deleted: boolean;
  map?: MapInfo;
}

/**
 * API 사용량 통계
 */
export interface UsageStats {
  total_calls: number;
  calls_today: number;
  calls_this_week: number;
  calls_this_month: number;
  most_used_endpoint?: string;
  average_response_time_ms?: number;
  success_rate?: number;
}

/**
 * 시간별 사용량
 */
export interface HourlyUsage {
  hour: string;
  count: number;
}

/**
 * 일별 사용량
 */
export interface DailyUsage {
  date: string;
  count: number;
}

/**
 * 엔드포인트별 사용량
 */
export interface EndpointUsage {
  endpoint: string;
  count: number;
  average_response_time_ms: number;
}

/**
 * Dashboard 통계 데이터
 */
export interface DashboardStats {
  usage: UsageStats;
  hourly_usage: HourlyUsage[];
  daily_usage: DailyUsage[];
  endpoint_usage: EndpointUsage[];
  recent_uploads: UserImage[];
}
