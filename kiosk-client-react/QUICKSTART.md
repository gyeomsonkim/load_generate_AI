# 빠른 시작 가이드 (React + TypeScript)

## 1. 백엔드 서버 실행

터미널 1:
```bash
cd /Users/ktg/Desktop/load_generate_ai/pathfinding-server
source ../venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

확인: `http://localhost:8000/docs`

## 2. 지도 업로드 (처음 한 번만)

Swagger UI에서 (`http://localhost:8000/docs`):

1. **POST /api/v1/maps/upload**
2. 지도 이미지 파일 업로드
3. 전처리 완료 대기
4. **GET /api/v1/maps/** 로 `preprocessing_status: "processed"` 확인

## 3. React 앱 실행

터미널 2:
```bash
cd /Users/ktg/Desktop/load_generate_ai/kiosk-client-react

# 의존성 설치 (처음 한 번만)
npm install

# 개발 서버 실행
npm run dev
```

자동으로 브라우저 열림: `http://localhost:5173`

## 4. 사용 방법

1. ✅ 지도 자동 로드
2. 🟢 첫 번째 클릭 → 출발지 (녹색)
3. 🔴 두 번째 클릭 → 도착지 (빨간색)
4. 🔵 경로 자동 표시 (파란색)
5. 🔄 "다시 시작" 버튼으로 리셋

## 5. 개발 명령어

```bash
# 개발 서버 (HMR)
npm run dev

# 타입 체크
npm run build

# 프로덕션 빌드
npm run build
npm run preview

# 의존성 설치
npm install
```

## 문제 해결

### "사용 가능한 지도가 없습니다"
→ 2번 단계에서 지도 업로드 및 전처리

### CORS 에러
→ 백엔드 서버가 `http://localhost:8000`에서 실행 중인지 확인

### TypeScript 에러
→ `npm install` 재실행

### 포트 충돌
→ `vite.config.ts`에서 포트 변경 또는 기존 프로세스 종료

## 환경 변수

`.env` 파일 (이미 생성됨):
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 디버깅

브라우저 개발자 도구 (F12):
- **Console**: 로그 및 에러 확인
- **Network**: API 요청/응답 확인
- **React DevTools**: 컴포넌트 상태 확인

## 프로젝트 구조

```
src/
├── types/          # TypeScript 타입
├── config/         # 설정
├── services/       # API 서비스
├── hooks/          # 커스텀 훅
├── components/     # React 컴포넌트
├── utils/          # 유틸리티
└── styles/         # CSS
```

## 다음 단계

- Vanilla JS 버전과 비교: `../kiosk-client/`
- 백엔드 API 문서: `http://localhost:8000/docs`
- React DevTools 설치: Chrome 확장 프로그램
