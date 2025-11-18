# Dashboard API Quick Start Guide

## 🚀 빠른 시작 (5분 완료)

### 1단계: 서버 시작

```bash
cd pathfinding-server
source venv_py311/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2단계: 기본 API 키 생성

```bash
./venv_py311/bin/python create_default_api_key.py
```

**예상 출력:**
```
✅ 기본 API 키 생성 완료!
   - API Key: 000000
```

### 3단계: API 테스트

```bash
# Dashboard 통계 확인
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "X-API-Key: 000000" | jq

# API 문서 열기
open http://localhost:8000/docs
```

---

## 📋 주요 엔드포인트

### 인증
```bash
# API 키 검증
POST /api/v1/auth/verify
Body: {"api_key": "000000"}
```

### Dashboard
```bash
# 종합 통계
GET /api/v1/dashboard/stats
Header: X-API-Key: 000000

# 이미지 목록
GET /api/v1/dashboard/images
Header: X-API-Key: 000000

# 사용량 (week|day|month)
GET /api/v1/dashboard/usage?period=week
Header: X-API-Key: 000000
```

### API 키 관리
```bash
# 키 목록
GET /api/v1/dashboard/api-keys
Header: X-API-Key: 000000

# 키 생성
POST /api/v1/dashboard/api-keys
Header: X-API-Key: 000000

# 키 삭제
DELETE /api/v1/dashboard/api-keys/{id}
Header: X-API-Key: 000000
```

---

## 🔗 클라이언트 연동

### Next.js Dashboard

```typescript
// docs-site에서 사용
import { apiClient } from '@/lib/api/client';

// 통계 조회
const stats = await apiClient.dashboard.getStats();

// 이미지 목록
const images = await apiClient.dashboard.getImages();
```

---

## 📚 상세 문서

- **전체 API 문서:** `DASHBOARD_API.md`
- **구현 보고서:** `IMPLEMENTATION_SUMMARY.md`
- **Swagger UI:** http://localhost:8000/docs

---

## 🧪 테스트

```bash
# 자동 테스트 실행
./test_dashboard_api.sh
```

---

## 🆘 문제 해결

### API 키 에러
```bash
# 키 다시 생성
./venv_py311/bin/python create_default_api_key.py
```

### 데이터베이스 초기화
```bash
# 데이터베이스 재설정
rm data.db  # SQLite인 경우
./venv_py311/bin/python create_default_api_key.py
```

---

**완료! Dashboard API 준비 완료 ✅**
