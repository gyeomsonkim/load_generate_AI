# Dashboard API Documentation

FastAPI 기반 Dashboard API 구현 완료 문서입니다.

## 📋 목차

1. [구현된 기능](#구현된-기능)
2. [데이터베이스 스키마](#데이터베이스-스키마)
3. [API 엔드포인트](#api-엔드포인트)
4. [사용 방법](#사용-방법)
5. [테스트 방법](#테스트-방법)

---

## ✅ 구현된 기능

### Phase 1: 필수 기능
- [x] `api_keys` 테이블 생성
- [x] `api_usage` 테이블 생성
- [x] `user_images` 테이블 생성
- [x] POST `/api/v1/auth/verify` - API 키 검증
- [x] POST `/api/v1/dashboard/api-keys` - API 키 생성
- [x] GET `/api/v1/dashboard/api-keys` - API 키 목록

### Phase 2: Dashboard 기능
- [x] GET `/api/v1/dashboard/stats` - Dashboard 통계
- [x] GET `/api/v1/dashboard/images` - 이미지 목록
- [x] GET `/api/v1/dashboard/usage` - 사용량 조회

### Phase 3: 부가 기능
- [x] DELETE `/api/v1/dashboard/api-keys/{key_id}` - API 키 삭제
- [x] API 사용량 추적 미들웨어
- [x] 자동 사용량 기록

---

## 🗄️ 데이터베이스 스키마

### 1. api_keys 테이블

```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(6) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    usage_count INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP
);

CREATE INDEX idx_api_keys_key ON api_keys(key);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

### 2. api_usage 테이블

```sql
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_id INTEGER NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    request_data JSON,
    user_agent VARCHAR(255),
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE CASCADE
);

CREATE INDEX idx_api_usage_api_key_id ON api_usage(api_key_id);
CREATE INDEX idx_api_usage_timestamp ON api_usage(timestamp);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
```

### 3. user_images 테이블

```sql
CREATE TABLE user_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_id INTEGER NOT NULL,
    map_id VARCHAR NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE CASCADE,
    FOREIGN KEY (map_id) REFERENCES maps(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_images_api_key_id ON user_images(api_key_id);
CREATE INDEX idx_user_images_map_id ON user_images(map_id);
CREATE INDEX idx_user_images_is_deleted ON user_images(is_deleted);
```

---

## 📡 API 엔드포인트

### 🔐 인증 API

#### POST `/api/v1/auth/verify`

API 키를 검증합니다.

**Request Body:**
```json
{
  "api_key": "000000"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "key_info": {
    "id": 1,
    "key": "000000",
    "is_active": true,
    "usage_count": 150,
    "created_at": "2024-11-18T12:00:00Z",
    "last_used_at": "2024-11-18T14:30:00Z"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "valid": false,
  "key_info": null
}
```

---

### 📊 Dashboard API

#### GET `/api/v1/dashboard/stats`

Dashboard 종합 통계를 조회합니다.

**Headers:**
```
X-API-Key: {api_key}
```

**Response (200 OK):**
```json
{
  "usage": {
    "total_calls": 1250,
    "calls_today": 45,
    "calls_this_week": 320,
    "calls_this_month": 890,
    "most_used_endpoint": "/api/v1/pathfinding/route",
    "average_response_time_ms": 125.5,
    "success_rate": 98.5
  },
  "hourly_usage": [
    {
      "hour": "2024-11-18T00:00:00Z",
      "count": 12
    }
  ],
  "daily_usage": [
    {
      "date": "2024-11-18",
      "count": 45
    }
  ],
  "endpoint_usage": [
    {
      "endpoint": "/api/v1/pathfinding/route",
      "count": 650,
      "average_response_time_ms": 145.2
    }
  ],
  "recent_uploads": [
    {
      "id": 1,
      "api_key_id": 1,
      "map_id": "abc-123",
      "upload_timestamp": "2024-11-18T14:30:00Z",
      "is_deleted": false,
      "map": {
        "id": "abc-123",
        "name": "Central Park",
        "map_type": "park",
        "preprocessing_status": "completed",
        "created_at": "2024-11-18T14:30:00Z",
        "original_image_url": "/media/maps/abc-123/original.jpg",
        "processed_image_url": "/media/maps/abc-123/processed.jpg",
        "width": 1920,
        "height": 1080,
        "scale_meters_per_pixel": 0.5
      }
    }
  ]
}
```

#### GET `/api/v1/dashboard/images`

업로드한 모든 이미지 목록을 조회합니다.

**Headers:**
```
X-API-Key: {api_key}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "api_key_id": 1,
    "map_id": "abc-123",
    "upload_timestamp": "2024-11-18T14:30:00Z",
    "is_deleted": false,
    "map": {
      "id": "abc-123",
      "name": "Central Park",
      "map_type": "park",
      "preprocessing_status": "completed",
      "created_at": "2024-11-18T14:30:00Z",
      "original_image_url": "/media/maps/abc-123/original.jpg",
      "processed_image_url": "/media/maps/abc-123/processed.jpg",
      "width": 1920,
      "height": 1080,
      "scale_meters_per_pixel": 0.5
    }
  }
]
```

#### GET `/api/v1/dashboard/usage`

기간별 API 사용량을 조회합니다.

**Headers:**
```
X-API-Key: {api_key}
```

**Query Parameters:**
- `period`: `day` | `week` | `month` (기본값: `week`)

**Response (200 OK):**
```json
[
  {
    "date": "2024-11-18",
    "count": 45
  },
  {
    "date": "2024-11-17",
    "count": 52
  }
]
```

---

### 🔑 API 키 관리 API

#### GET `/api/v1/dashboard/api-keys`

모든 API 키 목록을 조회합니다.

**Headers:**
```
X-API-Key: {api_key}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "key": "000000",
    "is_active": true,
    "usage_count": 150,
    "created_at": "2024-11-01T10:00:00Z",
    "last_used_at": "2024-11-18T14:30:00Z"
  }
]
```

#### POST `/api/v1/dashboard/api-keys`

새 API 키를 생성합니다.

**Headers:**
```
X-API-Key: {api_key}
```

**Request Body (Optional):**
```json
{
  "name": "Production Key"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "key": "345678",
  "is_active": true,
  "usage_count": 0,
  "created_at": "2024-11-18T15:00:00Z",
  "last_used_at": null
}
```

#### DELETE `/api/v1/dashboard/api-keys/{key_id}`

API 키를 삭제합니다 (Soft delete).

**Headers:**
```
X-API-Key: {api_key}
```

**Response (200 OK):**
```json
{
  "message": "API key deleted successfully"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "현재 사용 중인 API 키는 삭제할 수 없습니다"
}
```

---

## 🚀 사용 방법

### 1. 서버 시작

```bash
cd pathfinding-server

# 가상 환경 활성화
source venv_py311/bin/activate

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

### 2. 기본 API 키 생성

```bash
# 기본 API 키 (000000) 생성
python create_default_api_key.py
```

출력:
```
==================================================
기본 API 키 생성 스크립트
==================================================
✅ 기본 API 키 생성 완료!
   - API Key: 000000
   - ID: 1
   - 사용법: X-API-Key: 000000
==================================================
```

### 3. API 사용 예시

#### API 키 검증
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "000000"}'
```

#### Dashboard 통계 조회
```bash
curl -X GET http://localhost:8000/api/v1/dashboard/stats \
  -H "X-API-Key: 000000"
```

#### 새 API 키 생성
```bash
curl -X POST http://localhost:8000/api/v1/dashboard/api-keys \
  -H "X-API-Key: 000000" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Key"}'
```

---

## 🧪 테스트 방법

### 자동 테스트 스크립트 실행

```bash
./test_dashboard_api.sh
```

이 스크립트는 다음을 자동으로 테스트합니다:
1. API 키 검증
2. 새 API 키 생성
3. API 키 목록 조회
4. Dashboard 통계 조회
5. 이미지 목록 조회
6. 주간 사용량 조회
7. 일일 사용량 조회
8. API 키 삭제

### 수동 테스트

#### 1. API 키 검증
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "000000"}' | jq
```

#### 2. Dashboard 통계
```bash
curl -X GET http://localhost:8000/api/v1/dashboard/stats \
  -H "X-API-Key: 000000" | jq
```

#### 3. 사용량 조회 (주간)
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/usage?period=week" \
  -H "X-API-Key: 000000" | jq
```

---

## 🔧 미들웨어

### API 사용량 추적 미들웨어

모든 API 요청이 자동으로 추적됩니다:

- **추적 항목:**
  - API 키 ID
  - 엔드포인트 경로
  - HTTP 메서드
  - 응답 상태 코드
  - 응답 시간 (밀리초)
  - 타임스탬프
  - User-Agent

- **동작 방식:**
  1. 요청 수신 시 시작 시간 기록
  2. 요청 처리
  3. 응답 시간 계산
  4. `api_usage` 테이블에 비동기로 기록
  5. `api_keys.usage_count` 자동 증가

---

## 📝 추가 정보

### 보안 고려사항

1. **API 키 보호:**
   - HTTPS 사용 권장
   - API 키는 환경 변수로 관리
   - 프론트엔드에서는 localStorage에 안전하게 저장

2. **Rate Limiting:**
   - 현재 미구현 (Phase 4에서 추가 권장)
   - `slowapi` 라이브러리 사용 권장

3. **CORS 설정:**
   - `app/config.py`에서 허용 origin 설정
   - 프로덕션에서는 특정 도메인만 허용

### 성능 최적화

1. **데이터베이스 인덱스:**
   - 모든 주요 쿼리 컬럼에 인덱스 설정됨
   - `timestamp`, `api_key_id`, `endpoint` 등

2. **비동기 처리:**
   - SQLAlchemy AsyncSession 사용
   - 모든 DB 쿼리 비동기 처리

3. **캐싱:**
   - 추후 Redis 추가 권장
   - Dashboard 통계는 캐싱 대상

### 데이터 정책

1. **Soft Delete:**
   - API 키 삭제 시 `is_active = False`
   - 사용 기록 유지

2. **데이터 보관:**
   - `api_usage` 테이블은 급격히 증가
   - 월별 아카이빙 권장

3. **개인정보:**
   - User-Agent만 저장
   - IP 주소는 저장하지 않음

---

## 🐛 문제 해결

### 1. API 키가 동작하지 않음

```bash
# API 키 확인
curl -X GET http://localhost:8000/api/v1/dashboard/api-keys \
  -H "X-API-Key: 000000"
```

### 2. 데이터베이스 초기화

```bash
# 데이터베이스 삭제 후 재생성
rm data.db
python create_default_api_key.py
```

### 3. 미들웨어 로그 확인

```bash
# 서버 로그에서 API usage logged 확인
# app/middleware/usage_tracker.py 의 logger.debug 레벨을 INFO로 변경
```

---

## 📚 관련 문서

- **프론트엔드 연동:** `docs-site/lib/api/client.ts`
- **타입 정의:** `docs-site/types/`
- **API 문서:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🎯 다음 단계

1. **Redis 캐싱 추가:**
   - Dashboard 통계 캐싱
   - API 응답 캐싱

2. **Rate Limiting:**
   - API 키별 요청 제한
   - IP별 요청 제한

3. **Webhook 지원:**
   - 이미지 업로드 완료 시 알림
   - 처리 완료 시 콜백

4. **분석 기능:**
   - 사용 패턴 분석
   - 이상 탐지
   - 비용 추적

---

**구현 완료 일자:** 2024-11-18
**구현자:** Claude Code
**버전:** 1.0.0
