# Backend API 구현 요구사항

Dashboard 기능을 위해 FastAPI 백엔드에 추가로 구현이 필요한 API 엔드포인트 목록입니다.

## 📋 목차

1. [인증 API](#인증-api)
2. [Dashboard API](#dashboard-api)
3. [API 키 관리 API](#api-키-관리-api)
4. [데이터베이스 스키마](#데이터베이스-스키마)

---

## 🔐 인증 API

### 1. API 키 검증

**POST** `/api/v1/auth/verify`

6자리 API 키를 검증하고 로그인을 처리합니다.

#### Request Body
```json
{
  "api_key": "123456"
}
```

#### Response (200 OK)
```json
{
  "valid": true,
  "key_info": {
    "id": 1,
    "key": "123456",
    "is_active": true,
    "usage_count": 150,
    "created_at": "2024-11-17T12:00:00Z"
  }
}
```

#### Response (401 Unauthorized)
```json
{
  "error": "Invalid API key"
}
```

#### 구현 사항
- 6자리 숫자 키 검증
- 활성화 상태 확인
- 마지막 사용 시간 업데이트

---

## 📊 Dashboard API

### 1. Dashboard 통계 조회

**GET** `/api/v1/dashboard/stats`

**Headers:**
```
X-API-Key: {api_key}
```

Dashboard 메인 페이지에 표시할 종합 통계를 반환합니다.

#### Response (200 OK)
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
      "hour": "2024-11-17T00:00:00Z",
      "count": 12
    }
  ],
  "daily_usage": [
    {
      "date": "2024-11-17",
      "count": 45
    },
    {
      "date": "2024-11-16",
      "count": 52
    }
  ],
  "endpoint_usage": [
    {
      "endpoint": "/api/v1/pathfinding/route",
      "count": 650,
      "average_response_time_ms": 145.2
    },
    {
      "endpoint": "/api/v1/maps/upload",
      "count": 120,
      "average_response_time_ms": 320.5
    }
  ],
  "recent_uploads": [
    {
      "id": 1,
      "api_key_id": 1,
      "map_id": 5,
      "upload_timestamp": "2024-11-17T14:30:00Z",
      "is_deleted": false,
      "map": {
        "id": 5,
        "name": "Central Park",
        "map_type": "park",
        "processing_status": "completed",
        "created_at": "2024-11-17T14:30:00Z",
        "original_image_url": "/media/maps/5/original.jpg",
        "processed_image_url": "/media/maps/5/processed.jpg",
        "image_width": 1920,
        "image_height": 1080,
        "file_size": 2048576
      }
    }
  ]
}
```

#### 구현 사항
- 현재 API 키로 필터링
- 최근 7일간의 daily_usage 반환
- 최근 24시간의 hourly_usage 반환
- 최근 업로드 6개만 반환

---

### 2. 이미지 목록 조회

**GET** `/api/v1/dashboard/images`

**Headers:**
```
X-API-Key: {api_key}
```

사용자가 업로드한 모든 이미지 목록을 반환합니다.

#### Response (200 OK)
```json
[
  {
    "id": 1,
    "api_key_id": 1,
    "map_id": 5,
    "upload_timestamp": "2024-11-17T14:30:00Z",
    "is_deleted": false,
    "map": {
      "id": 5,
      "name": "Central Park",
      "map_type": "park",
      "processing_status": "completed",
      "created_at": "2024-11-17T14:30:00Z",
      "original_image_url": "/media/maps/5/original.jpg",
      "processed_image_url": "/media/maps/5/processed.jpg",
      "image_width": 1920,
      "image_height": 1080,
      "file_size": 2048576,
      "scale_meters_per_pixel": 0.5
    }
  }
]
```

#### 구현 사항
- 현재 API 키로 필터링
- 삭제되지 않은 이미지만 반환 (is_deleted = false)
- 최신 업로드 순으로 정렬
- Map 정보 조인하여 반환

---

### 3. API 사용량 조회

**GET** `/api/v1/dashboard/usage?period={period}`

**Headers:**
```
X-API-Key: {api_key}
```

**Query Parameters:**
- `period`: `day` | `week` | `month` (default: `week`)

기간별 API 사용량을 반환합니다.

#### Response (200 OK)
```json
[
  {
    "date": "2024-11-17",
    "count": 45
  },
  {
    "date": "2024-11-16",
    "count": 52
  },
  {
    "date": "2024-11-15",
    "count": 38
  }
]
```

#### 구현 사항
- `day`: 최근 24시간 (시간별)
- `week`: 최근 7일 (일별)
- `month`: 최근 30일 (일별)
- 현재 API 키로 필터링

---

## 🔑 API 키 관리 API

### 1. API 키 목록 조회

**GET** `/api/v1/dashboard/api-keys`

**Headers:**
```
X-API-Key: {api_key}
```

현재 사용자의 모든 API 키를 반환합니다.

#### Response (200 OK)
```json
[
  {
    "id": 1,
    "key": "123456",
    "is_active": true,
    "usage_count": 150,
    "created_at": "2024-11-01T10:00:00Z",
    "last_used_at": "2024-11-17T14:30:00Z"
  },
  {
    "id": 2,
    "key": "789012",
    "is_active": true,
    "usage_count": 45,
    "created_at": "2024-11-10T15:00:00Z",
    "last_used_at": "2024-11-17T12:00:00Z"
  }
]
```

#### 구현 사항
- 현재 API 키의 소유자로 필터링
- 생성일 기준 내림차순 정렬

---

### 2. API 키 생성

**POST** `/api/v1/dashboard/api-keys`

**Headers:**
```
X-API-Key: {api_key}
```

**Request Body** (선택사항)
```json
{
  "name": "Production Key"
}
```

새로운 6자리 API 키를 생성합니다.

#### Response (201 Created)
```json
{
  "id": 3,
  "key": "345678",
  "is_active": true,
  "usage_count": 0,
  "created_at": "2024-11-17T15:00:00Z",
  "last_used_at": null
}
```

#### 구현 사항
- 6자리 랜덤 숫자 생성
- 중복 체크 (재생성 로직)
- 현재 사용자와 연결

---

### 3. API 키 삭제

**DELETE** `/api/v1/dashboard/api-keys/{key_id}`

**Headers:**
```
X-API-Key: {api_key}
```

특정 API 키를 삭제합니다.

#### Response (200 OK)
```json
{
  "message": "API key deleted successfully"
}
```

#### Response (403 Forbidden)
```json
{
  "error": "Cannot delete the currently used API key"
}
```

#### 구현 사항
- 현재 사용 중인 키는 삭제 불가
- 소유자 확인
- Soft delete 권장 (is_active = false)

---

## 🗄️ 데이터베이스 스키마

### 1. api_keys 테이블 (신규)

```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(6) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP
);

CREATE INDEX idx_api_keys_key ON api_keys(key);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
```

---

### 2. api_usage 테이블 (신규)

```sql
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_data JSONB,
    user_agent VARCHAR(255)
);

CREATE INDEX idx_api_usage_api_key_id ON api_usage(api_key_id);
CREATE INDEX idx_api_usage_timestamp ON api_usage(timestamp);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
```

---

### 3. user_images 테이블 (신규)

```sql
CREATE TABLE user_images (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id) ON DELETE CASCADE,
    map_id INTEGER REFERENCES maps(id) ON DELETE CASCADE,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_user_images_api_key_id ON user_images(api_key_id);
CREATE INDEX idx_user_images_map_id ON user_images(map_id);
CREATE INDEX idx_user_images_is_deleted ON user_images(is_deleted);
```

---

### 4. maps 테이블 수정 (기존)

기존 `maps` 테이블에 다음 필드가 없다면 추가:

```sql
ALTER TABLE maps ADD COLUMN IF NOT EXISTS original_image_url VARCHAR(500);
ALTER TABLE maps ADD COLUMN IF NOT EXISTS processed_image_url VARCHAR(500);
```

---

## 🔄 미들웨어 구현

### API 사용량 추적 미들웨어

모든 API 요청에 대해 자동으로 사용량을 추적하는 미들웨어 구현이 필요합니다.

```python
@app.middleware("http")
async def track_api_usage(request: Request, call_next):
    start_time = time.time()

    # API 키 추출
    api_key = request.headers.get("X-API-Key")

    # 요청 처리
    response = await call_next(request)

    # 응답 시간 계산
    response_time_ms = (time.time() - start_time) * 1000

    # 사용량 기록 (비동기로 처리)
    if api_key:
        await log_api_usage(
            api_key=api_key,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            user_agent=request.headers.get("User-Agent")
        )

    return response
```

---

## 🎯 구현 우선순위

### Phase 1: 필수 기능
1. ✅ `api_keys` 테이블 생성
2. ✅ `user_images` 테이블 생성
3. ✅ `api_usage` 테이블 생성
4. ✅ POST `/api/v1/auth/verify` - API 키 검증
5. ✅ POST `/api/v1/dashboard/api-keys` - API 키 생성
6. ✅ GET `/api/v1/dashboard/api-keys` - API 키 목록

### Phase 2: Dashboard 기능
7. ✅ GET `/api/v1/dashboard/stats` - Dashboard 통계
8. ✅ GET `/api/v1/dashboard/images` - 이미지 목록
9. ✅ GET `/api/v1/dashboard/usage` - 사용량 조회

### Phase 3: 부가 기능
10. ✅ DELETE `/api/v1/dashboard/api-keys/{key_id}` - API 키 삭제
11. ✅ API 사용량 추적 미들웨어
12. ✅ `maps` 업로드 시 `user_images` 자동 생성

---

## 📝 추가 고려사항

### 보안
- API 키 생성 시 중복 체크 필수
- Rate limiting 구현 권장
- API 키별 사용 제한 설정 가능

### 성능
- `api_usage` 테이블이 급격히 커질 수 있으므로:
  - 파티셔닝 고려 (월별/주별)
  - 오래된 데이터 아카이빙
  - 인덱스 최적화

### 데이터 정책
- 삭제된 이미지 처리 방침 (Soft delete 권장)
- API 사용 기록 보관 기간 설정
- 개인정보 보호 정책 준수

---

## 🧪 테스트 시나리오

### 인증 테스트
```bash
# 1. API 키 생성
curl -X POST http://localhost:8000/api/v1/dashboard/api-keys \
  -H "X-API-Key: 000000"

# 2. API 키 검증
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"api_key": "123456"}'
```

### Dashboard 테스트
```bash
# 3. Dashboard 통계 조회
curl -X GET http://localhost:8000/api/v1/dashboard/stats \
  -H "X-API-Key: 123456"

# 4. 이미지 목록 조회
curl -X GET http://localhost:8000/api/v1/dashboard/images \
  -H "X-API-Key: 123456"

# 5. 사용량 조회
curl -X GET "http://localhost:8000/api/v1/dashboard/usage?period=week" \
  -H "X-API-Key: 123456"
```

---

## 📚 참고사항

### 기존 API와의 통합
- 기존 `/api/v1/maps/upload` 엔드포인트는 그대로 유지
- 업로드 시 `user_images` 테이블에 자동 추가
- `X-API-Key` 헤더로 사용자 식별

### 프론트엔드 연동
- API 클라이언트: `lib/api/client.ts`에 이미 구현됨
- 인증 스토어: `lib/store/auth.ts`에 구현됨
- 모든 타입 정의: `types/` 디렉토리에 준비됨

---

이 문서를 참고하여 FastAPI 백엔드를 구현하시면 됩니다.
문의사항이 있으시면 프론트엔드 코드를 참고하세요.
