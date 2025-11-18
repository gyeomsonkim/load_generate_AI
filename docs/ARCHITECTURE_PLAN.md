# ML 마이크로서비스 아키텍처 분리 계획

## 🎯 목표

ML 추론 기능을 독립된 FastAPI 서비스로 분리하여 확장성과 유지보수성 향상

---

## 📐 최종 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│ 1. ml-inference-server (신규 프로젝트, EC2)                    │
├──────────────────────────────────────────────────────────────┤
│ 목적: ML 모델 학습 + 추론 API 제공                              │
│                                                               │
│ 디렉토리 구조:                                                 │
│ ml-inference-server/                                         │
│ ├── app/                                                     │
│ │   ├── main.py              # FastAPI 앱                    │
│ │   ├── api/                                                │
│ │   │   └── inference.py     # 추론 API                      │
│ │   ├── core/                                               │
│ │   │   ├── model.py         # 모델 로딩/추론                │
│ │   │   └── preprocessing.py # 이미지 전처리                 │
│ │   └── ml/                  # 학습 코드 (pathfinding-server에서 이동) │
│ │       ├── train.py                                         │
│ │       ├── data_pipeline.py                                │
│ │       └── segmentation/                                   │
│ ├── models/                  # 학습된 모델 파일               │
│ ├── requirements.txt                                         │
│ ├── .env                                                     │
│ └── README.md                                                │
│                                                               │
│ API 엔드포인트:                                                │
│ - POST /api/v1/segment      # 맵 세그멘테이션                 │
│ - POST /api/v1/predict      # 일반 추론                       │
│ - GET  /api/v1/health       # 헬스 체크                       │
│ - GET  /api/v1/model/info   # 모델 정보                       │
│                                                               │
│ 배포: EC2 (포트 8001)                                          │
│ 인스턴스: g4dn.xlarge (추론) or g4dn.2xlarge (학습+추론)        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 2. pathfinding-server (기존 프로젝트, 로컬/프로덕션)             │
├──────────────────────────────────────────────────────────────┤
│ 목적: 경로찾기 메인 서비스                                      │
│                                                               │
│ 변경 사항:                                                     │
│ ├── app/                                                     │
│ │   ├── services/                                           │
│ │   │   └── ml_client.py    # HTTP Client (신규)            │
│ │   └── core/                                               │
│ │       └── ml/ (삭제)       # → ml-inference-server로 이동   │
│ │                                                            │
│ │ ml_client.py 역할:                                         │
│ │ - HTTP 요청으로 ML 서버 호출                                 │
│ │ - 재시도 로직                                                │
│ │ - 캐싱                                                      │
│ │ - Fallback (CV 방식)                                       │
│ │                                                            │
│ └── .env                                                     │
│     └── ML_INFERENCE_URL=http://ml-server:8001              │
│                                                               │
│ 배포: 로컬 (개발) or EC2/ECS (프로덕션)                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 구현 단계

### Phase 1: ML Inference Server 생성 ✅

**1.1 프로젝트 구조 생성**
```bash
mkdir ml-inference-server
cd ml-inference-server

# 디렉토리 구조
ml-inference-server/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── inference.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── model.py
│   │   └── preprocessing.py
│   └── ml/  # pathfinding-server에서 복사
│       ├── __init__.py
│       ├── train.py
│       ├── data_pipeline.py
│       └── segmentation/
│           ├── __init__.py
│           ├── unet.py
│           └── segmentation_model.py
├── models/
├── datasets/
├── logs/
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── Dockerfile
```

**1.2 복사할 파일**
```
pathfinding-server → ml-inference-server

app/core/ml/train.py             → app/ml/train.py
app/core/ml/data_pipeline.py     → app/ml/data_pipeline.py
app/core/ml/base.py              → app/ml/base.py
app/core/ml/segmentation/*       → app/ml/segmentation/*
```

**1.3 신규 생성할 파일**
- `app/main.py`: FastAPI 앱
- `app/config.py`: 설정
- `app/api/inference.py`: 추론 API
- `app/core/model.py`: 모델 로더
- `app/core/preprocessing.py`: 전처리
- `requirements.txt`: 의존성
- `Dockerfile`: 컨테이너화
- `.env`: 환경변수

---

### Phase 2: Pathfinding Server 수정 ✅

**2.1 ML 코드 제거**
```bash
# 삭제할 디렉토리
rm -rf app/core/ml/
```

**2.2 HTTP Client 생성**
```
신규 파일:
- app/services/ml_client.py      # HTTP 클라이언트
- app/services/ml_fallback.py    # Fallback 로직 (CV)
```

**2.3 ml_service.py 수정**
```python
# 기존: 로컬 모델 호출
self.ml_model.segment_map(image)

# 변경: HTTP 요청
await ml_client.segment_map(image)
```

**2.4 .env 업데이트**
```bash
# 추가
ML_INFERENCE_URL=http://localhost:8001
ML_INFERENCE_TIMEOUT=30
ML_INFERENCE_RETRY=3
ENABLE_ML_FALLBACK=true
```

---

### Phase 3: EC2 배포 설정 ✅

**3.1 학습용 스크립트**
```bash
# scripts/train_on_ec2.sh
#!/bin/bash
# EC2에서 학습 실행

python -m app.ml.train \
  --generate_data \
  --epochs 50 \
  --batch_size 32 \
  --use_wandb

# 모델 S3 업로드
aws s3 cp models/ s3://your-bucket/models/ --recursive
```

**3.2 추론 서버 실행**
```bash
# scripts/run_inference_server.sh
#!/bin/bash
# 추론 서버 시작

uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 2
```

**3.3 Docker 설정**
```dockerfile
# Dockerfile
FROM pytorch/pytorch:2.0-cuda11.7-cudnn8-runtime

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**3.4 docker-compose.yml**
```yaml
version: '3.8'

services:
  ml-inference:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - ./models:/app/models
    environment:
      - ML_DEVICE=cuda
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 🔄 통신 흐름

```
┌─────────────┐                ┌──────────────────┐
│   사용자     │                │ Pathfinding API  │
└──────┬──────┘                └────────┬─────────┘
       │                                │
       │ 1. POST /api/v1/maps/upload   │
       │────────────────────────────────>
       │                                │
       │                                │ 2. HTTP POST
       │                                │    /api/v1/segment
       │                                ├────────────────────┐
       │                                │                    │
       │                        ┌───────▼──────────┐         │
       │                        │ ML Inference API │         │
       │                        │ (EC2, Port 8001) │         │
       │                        └───────┬──────────┘         │
       │                                │                    │
       │                                │ 3. 세그멘테이션     │
       │                                │    결과 반환        │
       │                                <────────────────────┘
       │                                │
       │ 4. 경로찾기 결과                │
       <────────────────────────────────│
       │                                │
```

---

## 📦 의존성 관리

### ml-inference-server/requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
torch==2.0.1
torchvision==0.15.2
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.1.0
albumentations==1.3.1
tensorboard==2.15.1
wandb==0.16.0
pydantic==2.5.0
python-multipart==0.0.6
httpx==0.25.1
```

### pathfinding-server/requirements.txt (업데이트)
```txt
# ML 관련 제거:
# torch
# torchvision
# tensorboard

# HTTP 클라이언트 추가:
httpx==0.25.1
tenacity==8.2.3  # 재시도
```

---

## 🔐 보안 고려사항

### 1. API 인증
```python
# ml-inference-server
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403)
```

### 2. 네트워크 격리
```bash
# EC2 Security Group
- Inbound: Port 8001 from pathfinding-server IP only
- Outbound: All
```

### 3. 환경변수 암호화
```bash
# AWS Systems Manager Parameter Store
aws ssm put-parameter \
  --name /ml-inference/api-key \
  --value "your-secret-key" \
  --type SecureString
```

---

## 📊 성능 최적화

### 1. 모델 캐싱
```python
# app/core/model.py
from functools import lru_cache

@lru_cache(maxsize=1)
def load_model():
    return torch.load("models/best_model.pth")
```

### 2. 배치 처리
```python
# 여러 요청 배치로 처리
async def batch_predict(images: List[Image]):
    batch = torch.stack(images)
    return model(batch)
```

### 3. GPU 최적화
```python
# Mixed Precision
with torch.cuda.amp.autocast():
    output = model(input)
```

---

## 🧪 테스트 계획

### 1. 단위 테스트
```python
# tests/test_inference.py
def test_segment_endpoint():
    response = client.post("/api/v1/segment", files={"image": ...})
    assert response.status_code == 200
```

### 2. 통합 테스트
```python
# tests/test_integration.py
async def test_end_to_end():
    # 1. ML 서버 호출
    ml_result = await ml_client.segment(image)

    # 2. 경로찾기
    path = pathfinder.find_path(ml_result)

    assert path is not None
```

### 3. 부하 테스트
```bash
# locust를 사용한 부하 테스트
locust -f tests/load_test.py --host http://ml-server:8001
```

---

## 📈 모니터링

### 1. 메트릭 수집
```python
from prometheus_client import Counter, Histogram

inference_requests = Counter('inference_requests_total', 'Total inference requests')
inference_duration = Histogram('inference_duration_seconds', 'Inference duration')
```

### 2. 로깅
```python
import logging

logger.info(f"Inference completed in {duration:.3f}s")
```

### 3. 헬스 체크
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "gpu_available": torch.cuda.is_available()
    }
```

---

## 💰 비용 최적화

### 1. 학습 vs 추론 인스턴스 분리

| 용도 | 인스턴스 | 실행 시간 | 시간당 비용 | 월 비용 |
|-----|---------|---------|-----------|---------|
| **학습** | g4dn.2xlarge | 2시간 (일회성) | $0.752 | ~$1.50 |
| **추론** | t3.medium (CPU) | 24/7 | $0.0416 | ~$30 |
| **추론** | g4dn.xlarge (GPU) | 24/7 | $0.526 | ~$380 |

**권장**: 학습은 g4dn.2xlarge (일회성), 추론은 t3.medium (CPU)

### 2. Auto Scaling
```yaml
# AWS Auto Scaling
min_instances: 1
max_instances: 3
target_cpu_utilization: 70%
```

### 3. Spot Instances
```bash
# 추론 서버를 Spot으로 실행 (최대 70% 할인)
aws ec2 run-instances \
  --instance-market-options "MarketType=spot" \
  ...
```

---

## 🚀 배포 워크플로우

### 개발 환경
```bash
# 로컬에서 ML 서버 실행
cd ml-inference-server
uvicorn app.main:app --port 8001

# 메인 서버 실행
cd pathfinding-server
uvicorn app.main:app --port 8000
```

### 프로덕션 환경
```bash
# 1. EC2에 ML 서버 배포
ssh ec2-user@ml-server
git clone https://github.com/your/ml-inference-server
cd ml-inference-server
docker-compose up -d

# 2. 메인 서버 배포
ssh ec2-user@pathfinding-server
git clone https://github.com/your/pathfinding-server
# .env 설정: ML_INFERENCE_URL=http://ml-server:8001
docker-compose up -d
```

---

## ✅ 검증 체크리스트

- [ ] ML 코드가 독립 프로젝트로 분리됨
- [ ] 추론 API가 FastAPI로 동작
- [ ] 메인 서버에서 HTTP로 ML 서버 호출
- [ ] 학습 스크립트가 독립적으로 실행 가능
- [ ] 에러 시 Fallback (CV) 동작
- [ ] Docker로 컨테이너화
- [ ] EC2 배포 가능
- [ ] 헬스 체크 및 모니터링
- [ ] API 문서 (Swagger)
- [ ] 단위/통합 테스트

---

## 📚 참고 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [PyTorch 배포 가이드](https://pytorch.org/serve/)
- [AWS EC2 GPU 인스턴스](https://aws.amazon.com/ec2/instance-types/g4/)
- [Docker 최적화](https://docs.docker.com/develop/dev-best-practices/)
