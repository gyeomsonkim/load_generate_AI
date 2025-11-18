# Dashboard API 클라이언트 연동 완료 ✅

**docs-site**가 pathfinding-server의 Dashboard API를 완벽하게 사용할 수 있도록 구현되었습니다.

---

## 📋 구현 현황

### ✅ 완료된 항목

#### 1. API 클라이언트 (lib/api/client.ts)
- ✅ Dashboard API 메서드 구현 (getDashboardStats, getDashboardImages, getApiUsage, getApiKeys, createApiKey, deleteApiKey)
- ✅ API 키 인증 (X-API-Key 헤더 자동 추가)
- ✅ localStorage를 통한 API 키 저장
- ✅ 에러 처리 및 응답 파싱

#### 2. 타입 정의 (types/dashboard.ts)
- ✅ DashboardStats, UsageStats, HourlyUsage, DailyUsage
- ✅ EndpointUsage, UserImage, MapInfo
- ✅ 백엔드 스키마와 완벽히 일치

#### 3. 인증 시스템
**로그인 페이지** (app/login/page.tsx):
- ✅ 6자리 API 키 입력 UI
- ✅ API 키 검증 (/api/v1/auth/verify)
- ✅ 자동 포커스 및 붙여넣기 지원
- ✅ 에러 처리

**Auth Store** (lib/store/auth.ts):
- ✅ Zustand를 통한 인증 상태 관리
- ✅ 로컬 스토리지 persistence
- ✅ login/logout 기능

**Dashboard Layout** (app/dashboard/layout.tsx):
- ✅ 인증 가드 (미인증 시 /login으로 리다이렉트)
- ✅ 사이드바 레이아웃

#### 4. Dashboard 페이지

**개요** (app/dashboard/page.tsx):
- ✅ apiClient.getDashboardStats() 호출
- ✅ 4개 통계 카드 (총 호출, 이번 주 호출, 업로드 이미지, 평균 응답시간)
- ✅ 2개 차트 (라인 차트, 바 차트)
- ✅ 최근 업로드 이미지 그리드
- ✅ 엔드포인트별 사용량 테이블
- ✅ 로딩 상태 및 에러 처리

**이미지 갤러리** (app/dashboard/images/page.tsx):
- ✅ apiClient.getDashboardImages() 호출
- ✅ 이미지 목록 그리드 레이아웃
- ✅ 이미지 비교 컴포넌트
- ✅ 빈 상태 처리

**사용량 통계** (app/dashboard/usage/page.tsx):
- ✅ apiClient.getApiUsage(period) 호출
- ✅ 기간 선택 (day/week/month)
- ✅ 통계 카드 (총 호출, 평균, 최대)
- ✅ 차트 2개 (라인, 바)
- ✅ 사용 패턴 분석

**API 키 관리** (app/dashboard/keys/page.tsx):
- ✅ apiClient.getApiKeys() 호출
- ✅ API 키 목록 표시
- ✅ 새 API 키 생성 (apiClient.createApiKey())
- ✅ API 키 삭제 (apiClient.deleteApiKey())
- ✅ 클립보드 복사 기능
- ✅ 사용 안내

#### 5. Dashboard 컴포넌트

**StatsCard** (components/dashboard/StatsCard.tsx):
- ✅ 통계 카드 컴포넌트
- ✅ 아이콘, 값, 변화량 표시
- ✅ 반응형 디자인

**UsageChart** (components/dashboard/UsageChart.tsx):
- ✅ recharts 기반 차트 컴포넌트
- ✅ 라인 차트 및 바 차트 지원
- ✅ 반응형 레이아웃
- ✅ 툴팁 및 범례

**ImageComparison** (components/dashboard/ImageComparison.tsx):
- ✅ 원본/전처리 이미지 비교 컴포넌트
- ✅ 탭 UI로 이미지 전환
- ✅ 이미지 메타데이터 표시
- ✅ Next.js Image 컴포넌트 사용

**DashboardSidebar** (components/dashboard/DashboardSidebar.tsx):
- ✅ 네비게이션 메뉴
- ✅ 로그아웃 버튼
- ✅ 홈으로 이동 링크
- ✅ 현재 페이지 하이라이트

---

## 🚀 사용 방법

### 1. 백엔드 서버 시작

```bash
cd pathfinding-server
source venv_py311/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2. API 키 생성

```bash
cd pathfinding-server
./venv_py311/bin/python create_default_api_key.py
```

**출력:**
```
✅ 기본 API 키 생성 완료!
   - API Key: 000000
```

### 3. 프론트엔드 서버 시작

```bash
cd docs-site
npm install  # 첫 실행 시
npm run dev
```

### 4. Dashboard 접속

1. **로그인**: http://localhost:3000/login
   - API 키 입력: `000000` (또는 생성한 API 키)
   - 자동으로 /dashboard로 리다이렉트

2. **Dashboard 페이지**:
   - 개요: http://localhost:3000/dashboard
   - 이미지: http://localhost:3000/dashboard/images
   - API 키: http://localhost:3000/dashboard/keys
   - 사용량: http://localhost:3000/dashboard/usage

---

## 🔄 API 호출 흐름

### 로그인 플로우

```
1. 사용자가 /login에서 API 키 입력
   ↓
2. apiClient.verifyApiKey(key) 호출
   → POST /api/v1/auth/verify
   ↓
3. 백엔드에서 API 키 검증
   ↓
4. 성공 시:
   - apiClient.setApiKey(key) → localStorage 저장
   - useAuthStore.login(key) → Zustand 상태 업데이트
   - router.push('/dashboard')
   ↓
5. Dashboard 페이지 로드
```

### Dashboard Stats 플로우

```
1. Dashboard 페이지 마운트
   ↓
2. useEffect에서 loadStats() 호출
   ↓
3. apiClient.getDashboardStats() 호출
   → GET /api/v1/dashboard/stats
   → Header: X-API-Key: 000000
   ↓
4. 백엔드에서:
   - verify_api_key() 의존성으로 API 키 검증
   - last_used_at 업데이트
   - 통계 집계 (총 호출, 시간별, 일별, 엔드포인트별)
   - 최근 업로드 이미지 조회
   ↓
5. 응답 데이터로 UI 렌더링
   - StatsCard 4개
   - UsageChart 2개
   - 최근 업로드 이미지 그리드
   - 엔드포인트 사용량 테이블
```

### API 키 생성 플로우

```
1. "새 API 키" 버튼 클릭
   ↓
2. apiClient.createApiKey() 호출
   → POST /api/v1/dashboard/api-keys
   → Header: X-API-Key: 000000
   ↓
3. 백엔드에서:
   - verify_api_key() 의존성으로 인증
   - 6자리 랜덤 키 생성
   - 중복 검사
   - DB에 저장
   ↓
4. 새 키를 keys 배열 앞에 추가
   ↓
5. UI 업데이트 (새 키 표시)
```

---

## 📊 데이터 흐름

### Client → Server

```typescript
// 1. API 키 설정 (로그인 시)
apiClient.setApiKey('000000');

// 2. API 호출 시 자동으로 헤더 추가
headers: {
  'Content-Type': 'application/json',
  'X-API-Key': '000000'
}

// 3. 백엔드에서 검증
verify_api_key() → ApiKey 객체 반환
```

### Server → Client

```typescript
// Dashboard 통계 응답
{
  usage: {
    total_calls: 150,
    calls_today: 12,
    calls_this_week: 45,
    // ...
  },
  hourly_usage: [...],
  daily_usage: [...],
  endpoint_usage: [...],
  recent_uploads: [...]
}
```

---

## 🔐 인증 관리

### 저장소 계층

1. **apiClient** (lib/api/client.ts):
   - localStorage에 'api_key' 저장
   - 모든 API 요청에 X-API-Key 헤더 추가

2. **useAuthStore** (lib/store/auth.ts):
   - Zustand persist를 통해 'auth-storage' 저장
   - isAuthenticated 상태 관리

### 인증 가드

```typescript
// Dashboard Layout
useEffect(() => {
  if (!isAuthenticated) {
    router.push('/login');
  }
}, [isAuthenticated, router]);
```

---

## 🎨 UI/UX 특징

### 로딩 상태
- 스피너 애니메이션
- 버튼 disabled 처리
- "확인 중..." 메시지

### 에러 처리
- 에러 아이콘 (AlertCircle)
- 에러 메시지 표시
- "다시 시도" 버튼

### 빈 상태
- 적절한 안내 메시지
- 아이콘 표시
- 다음 액션 가이드

### 반응형 디자인
- 모바일: 1열 그리드
- 태블릿: 2열 그리드
- 데스크톱: 3-4열 그리드

---

## 🧪 테스트 시나리오

### 1. 로그인 테스트

```bash
# 1. 백엔드 실행
cd pathfinding-server
uvicorn app.main:app --reload

# 2. API 키 생성
./venv_py311/bin/python create_default_api_key.py

# 3. 프론트엔드 실행
cd docs-site
npm run dev

# 4. 브라우저에서
http://localhost:3000/login
# API 키 입력: 000000
```

**예상 결과**:
- ✅ 로그인 성공
- ✅ /dashboard로 리다이렉트
- ✅ localStorage에 api_key 저장됨
- ✅ auth-storage에 상태 저장됨

### 2. Dashboard 통계 테스트

```bash
# Dashboard 페이지 접속
http://localhost:3000/dashboard
```

**예상 결과**:
- ✅ 4개 통계 카드 표시
- ✅ 2개 차트 표시
- ✅ 데이터가 없으면 "데이터가 없습니다" 표시

### 3. API 키 생성 테스트

```bash
# API 키 페이지 접속
http://localhost:3000/dashboard/keys

# "새 API 키" 버튼 클릭
```

**예상 결과**:
- ✅ 새 6자리 키 생성
- ✅ 목록에 추가됨
- ✅ 복사 버튼 동작
- ✅ 삭제 버튼 동작

### 4. 로그아웃 테스트

```bash
# 사이드바 "로그아웃" 버튼 클릭
```

**예상 결과**:
- ✅ /login으로 리다이렉트
- ✅ localStorage에서 api_key 삭제
- ✅ auth-storage 초기화

---

## 🔍 디버깅

### API 호출 확인

**브라우저 개발자 도구**:
```
Network 탭 → XHR/Fetch 필터
- Request Headers에 X-API-Key: 000000 확인
- Response 데이터 확인
```

**백엔드 로그**:
```bash
# 미들웨어 로그 확인
INFO:     127.0.0.1:xxxxx - "GET /api/v1/dashboard/stats HTTP/1.1" 200 OK

# API 사용량 기록 로그
API usage logged: endpoint=/api/v1/dashboard/stats
```

### 인증 문제

**localStorage 확인**:
```javascript
// 브라우저 콘솔
localStorage.getItem('api_key')  // "000000"
```

**auth-storage 확인**:
```javascript
// 브라우저 콘솔
localStorage.getItem('auth-storage')
// {"state":{"apiKey":"000000","isAuthenticated":true},"version":0}
```

---

## 📚 관련 문서

### 백엔드 문서
- `pathfinding-server/DASHBOARD_API.md` - API 상세 문서
- `pathfinding-server/API_ARCHITECTURE.md` - 시스템 아키텍처
- `pathfinding-server/IMPLEMENTATION_SUMMARY.md` - 구현 보고서

### 프론트엔드 코드
- `lib/api/client.ts` - API 클라이언트
- `types/dashboard.ts` - TypeScript 타입
- `app/dashboard/` - Dashboard 페이지
- `components/dashboard/` - Dashboard 컴포넌트

---

## ✨ 주요 기능

### 자동화된 기능
- ✅ API 키 자동 헤더 추가
- ✅ 자동 포커스 (로그인 입력)
- ✅ 자동 로그인 시도 (6자리 완성 시)
- ✅ 자동 리다이렉트 (인증 여부)
- ✅ 자동 사용량 추적 (백엔드 미들웨어)

### 사용자 경험
- ✅ 로딩 상태 표시
- ✅ 에러 처리 및 재시도
- ✅ 빈 상태 안내
- ✅ 클립보드 복사
- ✅ 반응형 디자인
- ✅ 다크 모드 준비 (Tailwind 클래스 사용)

---

## 🎯 다음 단계 (선택사항)

### Phase 4: 고급 기능
- [ ] 실시간 업데이트 (WebSocket 또는 polling)
- [ ] 차트 커스터마이징 (기간 선택, 필터)
- [ ] 이미지 편집 기능
- [ ] 사용량 알림 (임계값 설정)

### Phase 5: 최적화
- [ ] React Query로 데이터 캐싱
- [ ] 무한 스크롤 (이미지 목록)
- [ ] 이미지 lazy loading
- [ ] 차트 애니메이션

---

## 🆘 문제 해결

### "API 키가 유효하지 않습니다"

```bash
# 1. API 키 재생성
cd pathfinding-server
./venv_py311/bin/python create_default_api_key.py

# 2. 백엔드 재시작
uvicorn app.main:app --reload

# 3. 프론트엔드에서 다시 로그인
```

### "통계를 불러오는데 실패했습니다"

```bash
# 1. 백엔드 서버 실행 확인
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "X-API-Key: 000000"

# 2. CORS 설정 확인 (app/config.py)
allowed_origins = ["http://localhost:3000"]
```

### "로그인 후에도 Dashboard 접근 불가"

```bash
# 브라우저 콘솔에서 확인
localStorage.clear()  # 모든 저장소 초기화
# 다시 로그인
```

---

**구현 완료 ✅ | 통합 테스트 준비 완료 🚀**

*Last Updated: 2024-11-18*
