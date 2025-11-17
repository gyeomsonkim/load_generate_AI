// 인증 관련 타입 정의

/**
 * API 키 정보
 */
export interface ApiKeyInfo {
  id: number;
  key: string;
  name?: string;
  created_at: string;
  last_used_at?: string;
  is_active: boolean;
  usage_count: number;
  usage_limit?: number;
  metadata?: Record<string, unknown>;
}

/**
 * API 키 검증 요청
 */
export interface VerifyKeyRequest {
  key: string;
}

/**
 * API 키 검증 응답
 */
export interface VerifyKeyResponse {
  success: boolean;
  key?: string;
  api_key_info?: ApiKeyInfo;
  error?: string;
}

/**
 * 인증 상태
 */
export interface AuthState {
  isAuthenticated: boolean;
  apiKey: string | null;
  apiKeyInfo: ApiKeyInfo | null;
  setApiKey: (key: string, info: ApiKeyInfo) => void;
  clearAuth: () => void;
}
