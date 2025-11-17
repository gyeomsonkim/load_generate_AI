# 길찾기 키오스크 클라이언트 (React + TypeScript)

터치 기반 키오스크 인터페이스로 지도에서 경로를 찾는 React 애플리케이션입니다.

## 🚀 기술 스택

- **React 18** - UI 라이브러리
- **TypeScript** - 타입 안정성
- **Vite** - 빌드 도구 (빠른 HMR)
- **Leaflet** - 지도 렌더링
- **React Leaflet** - React용 Leaflet 통합

## 📁 프로젝트 구조

```
src/
├── types/              # TypeScript 타입 정의
│   └── index.ts
├── config/             # 앱 설정
│   └── index.ts
├── services/           # API 서비스 레이어
│   └── api.ts
├── hooks/              # 커스텀 React 훅
│   ├── useMapData.ts
│   ├── useMarkers.ts
│   └── usePathfinding.ts
├── components/         # React 컴포넌트
│   ├── StatusBar.tsx
│   ├── LoadingOverlay.tsx
│   └── MapView.tsx
├── utils/              # 유틸리티 함수
│   └── coordinates.ts
├── styles/             # CSS 스타일
│   ├── App.css
│   ├── StatusBar.css
│   ├── LoadingOverlay.css
│   └── MapView.css
├── App.tsx             # 메인 앱 컴포넌트
└── main.tsx            # 엔트리 포인트
```

## 🎯 핵심 기능

### 1. **타입 안정성**
- 모든 API 응답, 상태, 프로퍼티에 TypeScript 타입 적용
- 컴파일 타임 에러 감지
- IDE 자동완성 지원

### 2. **커스텀 훅 기반 상태 관리**
- `useMapData` - 지도 데이터 로딩 및 관리
- `useMarkers` - 시작/종료 마커 상태 관리
- `usePathfinding` - 경로 찾기 로직 및 상태

### 3. **컴포넌트 기반 아키텍처**
- `App` - 메인 오케스트레이션
- `MapView` - Leaflet 지도 렌더링
- `StatusBar` - 상태 표시 및 리셋 버튼
- `LoadingOverlay` - 로딩 상태 표시

### 4. **모던 React 패턴**
- 함수형 컴포넌트
- React Hooks (useState, useEffect, useCallback, useMemo, useRef)
- 메모이제이션으로 성능 최적화
- 타입 안전한 이벤트 핸들링

## 📦 설치 및 실행

### 1. 의존성 설치

```bash
cd kiosk-client-react
npm install
```

### 2. 환경 변수 설정

`.env` 파일이 자동 생성되어 있습니다:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 자동으로 열립니다: `http://localhost:5173`

### 4. 프로덕션 빌드

```bash
npm run build
npm run preview  # 빌드 결과 미리보기
```

## 🔧 사용 방법

### 백엔드 서버 실행 (필수)

```bash
cd ../pathfinding-server
python -m uvicorn app.main:app --reload --port 8000
```

### 지도 업로드 (처음 한 번)

Swagger UI (`http://localhost:8000/docs`)에서:
1. POST `/api/v1/maps/upload` 엔드포인트로 지도 업로드
2. 전처리 완료까지 대기
3. `preprocessing_status`가 `"processed"`인지 확인

### 키오스크 사용

1. 🗺️ 지도 자동 로드
2. 🟢 **첫 번째 터치**: 출발지 선택 (녹색 마커)
3. 🔴 **두 번째 터치**: 도착지 선택 (빨간 마커)
4. 🔵 **자동 경로 표시**: 파란색 폴리라인
5. 🔄 **리셋**: 우측 상단 "다시 시작" 버튼

## 🎨 스타일링

### CSS 구조

각 컴포넌트는 독립적인 CSS 파일을 가집니다:
- `App.css` - 전역 스타일
- `StatusBar.css` - 상태 바 스타일
- `LoadingOverlay.css` - 로딩 오버레이
- `MapView.css` - 지도 및 마커 스타일

### 터치 최적화

- `touch-action: none` - 기본 제스처 비활성화
- `user-scalable=no` - 의도하지 않은 줌 방지
- 큰 터치 영역 (30-40px+)

## 📄 라이선스

MIT License

## 🙋 문의

백엔드 API: `../pathfinding-server/README.md` 참조
