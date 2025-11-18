# 🚀 ML 기능 빠른 시작 가이드

## 📋 필수 사전 작업

### 1. 환경 설정 (자동)

```bash
# 설정 스크립트 실행
./setup_ml.sh
```

### 2. 환경 설정 (수동)

```bash
# 1. 디렉토리 생성
mkdir -p models datasets/maps/{images,masks}/{train,val,test} logs storage/processed

# 2. ML 패키지 설치
pip install torch torchvision opencv-python numpy scikit-image albumentations tqdm

# 또는 전체 설치
pip install -r requirements_ml.txt
```

## 🎯 단계별 실행

### Step 1: 테스트 데이터 생성

```bash
# Python으로 합성 데이터 100개 생성
python -c "
from app.core.ml.data_pipeline import DatasetGenerator
generator = DatasetGenerator('datasets/maps', num_samples=100)
generator.generate_dataset()
"
```

### Step 2: 모델 학습 (선택사항)

```bash
# 간단한 학습 (50 epochs)
python -m app.core.ml.train \
    --data_dir datasets/maps \
    --model_type unet \
    --epochs 50 \
    --batch_size 8

# 데이터 생성과 학습 동시에
python -m app.core.ml.train \
    --generate_data \
    --epochs 50
```

### Step 3: 서버 실행

```bash
# FastAPI 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: ML 기능 테스트

```bash
# 1. ML 서비스 상태 확인
curl http://localhost:8000/api/v1/ml/status

# 2. 헬스 체크
curl http://localhost:8000/api/v1/ml/health

# 3. A/B 테스트 활성화
curl -X POST http://localhost:8000/api/v1/ml/ab-test/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "ml_ratio": 0.3}'
```

## ⚙️ 설정 옵션

### .env 파일 설정

```bash
# ML 기능 활성화/비활성화
ENABLE_ML=true

# 사용할 모델 선택
ML_MODEL_TYPE=unet  # unet, attention_unet, deeplabv3plus

# 디바이스 선택
ML_DEVICE=cpu  # cpu, cuda, mps

# A/B 테스팅
AB_TEST_ENABLED=false
AB_TEST_ML_RATIO=0.3
```

## 🎨 사용 예제

### 1. 지도 업로드 및 자동 처리

```bash
curl -X POST http://localhost:8000/api/v1/maps/upload \
  -F "file=@my_map.png" \
  -F "name=Test Map" \
  -F "description=ML test"
```

### 2. 처리 모드 변경

```bash
# ML 전용 모드
curl -X POST http://localhost:8000/api/v1/ml/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "ml_only"}'

# Hybrid 모드 (권장)
curl -X POST http://localhost:8000/api/v1/ml/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "hybrid"}'
```

### 3. A/B 테스트 메트릭 확인

```bash
curl http://localhost:8000/api/v1/ml/ab-test/metrics
```

## 🐛 문제 해결

### ImportError 발생

```bash
# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:/Users/ktg/Desktop/load_generate_ai/pathfinding-server"

# 또는 프로젝트 루트에서 실행
cd /Users/ktg/Desktop/load_generate_ai/pathfinding-server
python -m app.core.ml.train --help
```

### 모델 없이 실행

```bash
# ML 비활성화 모드로 실행 (CV만 사용)
ENABLE_ML=false uvicorn app.main:app --reload
```

### GPU 메모리 부족

```bash
# 배치 크기 줄이기
python -m app.core.ml.train --batch_size 4 --epochs 50

# CPU 사용
ML_DEVICE=cpu python -m app.core.ml.train --epochs 50
```

## 📊 성능 확인

### 모델 벤치마크

```bash
curl -X POST "http://localhost:8000/api/v1/ml/model/benchmark?input_shape=1,3,512,512&iterations=100"
```

### 모델 정보

```bash
curl http://localhost:8000/api/v1/ml/model/info
```

## 📁 디렉토리 구조

```
pathfinding-server/
├── app/
│   └── core/
│       └── ml/
│           ├── __init__.py
│           ├── base.py
│           ├── data_pipeline.py
│           ├── train.py
│           └── segmentation/
│               ├── __init__.py
│               ├── unet.py
│               └── segmentation_model.py
├── models/                    # 학습된 모델 저장
│   └── map_segmentation_unet/
│       └── best_model.pth
├── datasets/                  # 학습 데이터
│   └── maps/
│       ├── images/
│       │   ├── train/
│       │   ├── val/
│       │   └── test/
│       └── masks/
│           ├── train/
│           ├── val/
│           └── test/
├── logs/                      # TensorBoard 로그
└── storage/                   # 처리된 이미지
    └── processed/
```

## 🎓 추가 학습

- 상세 가이드: `ML_IMPLEMENTATION_GUIDE.md`
- API 문서: http://localhost:8000/docs
- 모니터링: `tensorboard --logdir logs`

## 💡 팁

1. **처음 사용**: `--generate_data` 옵션으로 합성 데이터 생성
2. **빠른 테스트**: `--epochs 10` 으로 빠르게 테스트
3. **프로덕션**: 실제 데이터로 최소 100 epochs 학습 권장
4. **Hybrid 모드**: ML 신뢰도가 낮으면 자동으로 CV 사용
5. **A/B 테스트**: 30% ML로 시작해서 점진적으로 증가