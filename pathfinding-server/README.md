# 🗺️ AI 기반 길찾기 서버

지도 이미지를 업로드하고 AI/ML을 활용하여 최적 경로를 찾는 서버입니다.

## 🚀 Phase 1 완료 기능

### ✅ 구현 완료
- 이미지 업로드 API (`POST /api/v1/maps/upload`)
- 이미지 전처리 시스템 (OpenCV 기반)
- 보행 가능 영역 자동 감지
- 장애물 자동 검출
- 네비게이션 그리드 생성
- PostgreSQL 데이터베이스 통합
- Docker 환경 구성

### 📊 전처리 프로세스
1. **그레이스케일 변환** - 이미지를 흑백으로 변환
2. **이진화 처리** - 적응형 임계값을 사용한 이진 이미지 생성
3. **엣지 검출** - Canny 알고리즘으로 경계선 검출
4. **보행 가능 영역 추출** - 모폴로지 연산으로 보행 가능 영역 식별
5. **그리드 생성** - 길찾기용 저해상도 그리드 생성
6. **장애물 검출** - 연결된 구성 요소 분석
7. **입구 지점 감지** - 이미지 경계에서 접근 가능 지점 찾기

## 🛠️ 설치 및 실행

### 1. 로컬 실행 (Python)

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# PostgreSQL 설치 및 실행 (별도)
# 데이터베이스 생성: CREATE DATABASE pathfinding_db;

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 DB 연결 정보 설정

# 서버 실행
cd pathfinding-server
python -m app.main
```

### 2. Docker 실행 (권장)

```bash
# Docker Compose로 전체 스택 실행
cd pathfinding-server/docker
docker-compose up -d

# 로그 확인
docker-compose logs -f app

# 서버 접속
# API 문서: http://localhost:8000/docs
# 헬스체크: http://localhost:8000/api/v1/health
```

## 📡 API 사용 예시

### 1. 지도 업로드

```bash
curl -X POST "http://localhost:8000/api/v1/maps/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@park_map.jpg" \
  -F "name=Central Park" \
  -F "description=공원 지도" \
  -F "map_type=park" \
  -F "scale_meters_per_pixel=0.5"
```

### 2. 지도 목록 조회

```bash
curl -X GET "http://localhost:8000/api/v1/maps/"
```

### 3. 특정 지도 조회

```bash
curl -X GET "http://localhost:8000/api/v1/maps/{map_id}"
```

## 🎯 Phase 2 계획 (ML/DL 통합)

### 주요 목표
1. **딥러닝 모델 통합**
   - CNN 기반 보행로 세그멘테이션
   - 장애물 분류 모델 (건물, 물, 계단 등)
   - 경로 품질 예측 모델

2. **A* 길찾기 알고리즘 구현**
   - 그리드 기반 경로 탐색
   - 휴리스틱 함수 최적화
   - 다중 경로 생성

3. **길찾기 API 엔드포인트**
   - `POST /api/v1/pathfinding/route` - 기본 경로 찾기
   - `POST /api/v1/pathfinding/multi-route` - 다중 경유지
   - `GET /api/v1/pathfinding/alternatives` - 대체 경로

### 구현 우선순위
1. A* 알고리즘 기본 구현
2. 경로 찾기 API 엔드포인트
3. 경로 시각화 (SVG/Polyline)
4. Redis 캐싱 통합
5. ML 모델 훈련 및 통합

## 🚀 Phase 3 계획 (고급 기능)

### 주요 기능
1. **실시간 경로 업데이트** (WebSocket)
2. **다중 사용자 지원**
3. **경로 최적화 옵션**
   - 최단 거리
   - 접근성 우선
   - 경치 좋은 경로
4. **3D 지도 지원**
5. **모바일 SDK**

### 성능 최적화
- GPU 가속 (CUDA)
- 분산 처리 (Celery)
- 캐싱 최적화
- CDN 통합

## 📈 확장성 고려사항

### 인프라
- **AWS 배포**: EC2, RDS, S3, CloudFront
- **Docker 컨테이너화**: 완료
- **Kubernetes**: 자동 스케일링
- **로드 밸런싱**: Nginx/ALB

### 데이터베이스
- **읽기 전용 복제본**: 조회 성능 향상
- **파티셔닝**: 대용량 데이터 처리
- **인덱싱 최적화**: 쿼리 성능 개선

### ML/DL
- **모델 버전 관리**: MLflow
- **분산 훈련**: Horovod/PyTorch Distributed
- **모델 서빙**: TorchServe/TensorFlow Serving
- **A/B 테스팅**: 모델 성능 비교

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이센스

MIT License

## 🔗 참고 자료

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenCV Python](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [A* Algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [PyTorch](https://pytorch.org/docs/stable/index.html)