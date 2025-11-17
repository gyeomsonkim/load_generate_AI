// API 관련 타입 정의

/**
 * 지도 타입
 */
export type MapType = 'park' | 'building' | 'campus' | 'other';

/**
 * 처리 상태
 */
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * 좌표
 */
export interface Point {
  x: number;
  y: number;
}

/**
 * 지도 메타데이터
 */
export interface MapMetadata {
  name: string;
  description?: string;
  map_type: MapType;
  scale_meters_per_pixel?: number;
}

/**
 * 지도 정보
 */
export interface MapInfo {
  id: number;
  name: string;
  description?: string;
  map_type: MapType;
  original_filename: string;
  file_size: number;
  image_width: number;
  image_height: number;
  scale_meters_per_pixel?: number;
  processing_status: ProcessingStatus;
  created_at: string;
  updated_at: string;
  original_image_url?: string;
  processed_image_url?: string;
  grid_data?: unknown;
  walkable_areas?: unknown;
  obstacles?: unknown;
}

/**
 * 지도 업로드 응답
 */
export interface UploadMapResponse {
  id: number;
  message: string;
  map: MapInfo;
}

/**
 * 경로 요청
 */
export interface PathfindingRequest {
  map_id: number;
  start: Point;
  end: Point;
  waypoints?: Point[];
}

/**
 * 경로 응답
 */
export interface PathfindingResponse {
  map_id: number;
  path: Point[];
  distance: number;
  estimated_time?: number;
}

/**
 * API 에러 응답
 */
export interface ApiError {
  error: string;
  detail?: string;
  status_code: number;
}

/**
 * 페이지네이션 정보
 */
export interface PaginationInfo {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * 페이지네이션 응답
 */
export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}
