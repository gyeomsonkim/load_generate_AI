# AI 길찾기 API - 문서 사이트

Next.js 15 + TypeScript로 구축된 AI 길찾기 API 문서 및 Dashboard 사이트입니다.

## 🚀 시작하기

### 필수 요구사항

- Node.js 18.17 이상
- npm 또는 yarn
- 실행 중인 FastAPI 백엔드 (포트 8000)

### 설치

```bash
# 의존성 설치
npm install

# 환경 변수 설정
cp .env.local.example .env.local
# .env.local 파일을 편집하여 API URL 설정

# 개발 서버 실행
npm run dev
```

개발 서버가 [http://localhost:3000](http://localhost:3000)에서 실행됩니다.

## 📁 프로젝트 구조

```
docs-site/
├── app/                    # Next.js App Router
│   ├── docs/              # 문서 페이지
│   ├── dashboard/         # Dashboard 페이지
│   └── api/               # API Routes
├── components/            # React 컴포넌트
│   ├── layout/           # 레이아웃 컴포넌트
│   ├── docs/             # 문서 컴포넌트
│   ├── dashboard/        # Dashboard 컴포넌트
│   └── home/             # 홈 컴포넌트
├── lib/                   # 유틸리티 및 라이브러리
│   ├── api/              # API 클라이언트
│   ├── utils/            # 유틸리티 함수
│   └── hooks/            # React Hooks
├── types/                 # TypeScript 타입 정의
└── public/               # 정적 파일
```

## 🔧 기술 스택

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Form Handling**: React Hook Form + Zod
- **Charts**: Recharts
- **Code Highlighting**: React Syntax Highlighter
- **Icons**: Lucide React

## 📝 주요 기능

### 홈 페이지 (/)
- 서비스 소개
- 주요 기능 안내
- 빠른 시작 가이드

### 문서 페이지 (/docs)
- API 레퍼런스
- JavaScript/Python 코드 예제
- 사용 가이드

### Dashboard (/dashboard)
- 6자리 키 기반 인증
- 업로드한 이미지 관리
- API 사용량 통계
- 원본/전처리 이미지 비교

## 🔐 인증

이 사이트는 6자리 API 키를 사용한 간단한 인증 시스템을 사용합니다:

1. Dashboard 접속 시 API 키 입력
2. 키 검증 후 localStorage에 저장
3. 이후 API 호출 시 자동으로 헤더에 포함

## 🛠️ 개발 명령어

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start

# 린트 검사
npm run lint
```

## 📚 환경 변수

`.env.local` 파일에서 다음 환경 변수를 설정하세요:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
DATABASE_URL=postgresql://user:password@localhost:5432/pathfinding_db
```

## 🚀 배포

### Vercel 배포 (권장)

```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel
```

### Docker 배포

```bash
# Docker 이미지 빌드
docker build -t docs-site .

# 컨테이너 실행
docker run -p 3000:3000 docs-site
```

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

MIT License

## 📞 문의

- Email: contact@example.com
- GitHub: https://github.com
