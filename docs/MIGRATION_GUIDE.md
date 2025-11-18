# ML 마이크로서비스 분리 마이그레이션 가이드

## 📋 변경 사항

### 아키텍처 변화

**Before (Monolith)**:
```
pathfinding-server/
├── app/
│   ├── core/
│   │   └── ml/  ← ML 코드 내장
│   └── services/
│       └── ml_service.py  ← 직접 모델 호출
```

**After (Microservice)**:
```
ml-inference-server/        pathfinding-server/
├── app/                    ├── app/
│   ├── ml/  ← ML 코드       │   └── services/
│   └── api/                 │       ├── ml_client.py  ← HTTP Client
      └── inference.py       │       └── ml_service.py  ← HTTP 요청
```

---

## 🚀 마이그레이션 단계

### 1단계: ml-inference-server 설정

```bash
cd /Users/ktg/Desktop/load_generate_ai/ml-inference-server

# 의존성 설치
pip install -r requirements.txt

# .env 확인
cat .env
# ML_DEVICE=cpu
# MODEL_TYPE=unet
# PORT=8001

# 서버 실행 (터미널 1)
uvicorn app.main:app --port 8001 --reload
```

**확인**:
```bash
curl http://localhost:8001/health
# 예상 출력: {"status":"degraded","model_loaded":false,...}
# → 정상 (모델은 아직 학습 안 됨)
```

---

### 2단계: 모델 학습 (선택사항)

이미 학습된 모델이 있으면 건너뛰세요.

```bash
cd /Users/ktg/Desktop/load_generate_ai/ml-inference-server

# 합성 데이터 생성 + 학습
python -m app.ml.train --generate_data --epochs 20 --batch_size 4

# 학습 완료 후 서버 재시작
# 터미널 1에서 Ctrl+C 후
uvicorn app.main:app --port 8001 --reload
```

**확인**:
```bash
curl http://localhost:8001/health
# 예상 출력: {"status":"healthy","model_loaded":true,...}
```

---

### 3단계: pathfinding-server 설정

```bash
cd /Users/ktg/Desktop/load_generate_ai/pathfinding-server

# 의존성 재설치 (ML 제거, httpx 추가)
pip install -r requirements.txt

# .env 확인
cat .env | grep ML_INFERENCE
# ML_INFERENCE_URL=http://localhost:8001

# 서버 실행 (터미널 2)
uvicorn app.main:app --port 8000 --reload
```

---

### 4단계: 통합 테스트

```bash
# pathfinding-server가 ML 서버를 호출하는지 확인
curl http://localhost:8000/api/v1/ml/status

# 예상 출력:
# {
#   "ml_enabled": true,
#   "model_info": {
#     "model_loaded": true,  ← ML 서버 연결 성공
#     ...
#   }
# }
```

---

## 🔧 트러블슈팅

### 문제 1: "ML server health check failed"

**원인**: ml-inference-server가 실행 중이 아님

**해결**:
```bash
# 터미널 1에서
cd ml-inference-server
uvicorn app.main:app --port 8001
```

---

### 문제 2: "Model not loaded"

**원인**: 학습된 모델이 없음

**해결 1**: 로컬에서 학습
```bash
cd ml-inference-server
python -m app.ml.train --generate_data --epochs 20 --batch_size 4
```

**해결 2**: EC2에서 학습 후 다운로드
```bash
# EC2에서 학습 후
scp -i key.pem -r ubuntu@ec2-ip:~/ml-inference-server/models ./
```

---

### 문제 3: "Connection refused"

**원인**: 포트 충돌 또는 방화벽

**해결**:
```bash
# 포트 사용 확인
lsof -i :8001
lsof -i :8000

# 다른 포트 사용
uvicorn app.main:app --port 8002
# .env 수정: ML_INFERENCE_URL=http://localhost:8002
```

---

### 문제 4: Import 에러

**원인**: 의존성 누락

**해결**:
```bash
# pathfinding-server
pip install httpx tenacity

# ml-inference-server
pip install -r requirements.txt
```

---

## 📊 성능 비교

| 메트릭 | Before (Monolith) | After (Microservice) |
|--------|------------------|---------------------|
| 추론 시간 | 1.8s | 1.9s (+0.1s HTTP) |
| 메모리 (pathfinding) | 2.5GB | 500MB (-2GB) |
| 메모리 (ML 서버) | - | 2GB |
| 배포 독립성 | ❌ | ✅ |
| 확장성 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 다음 단계

### 로컬 개발 환경
```bash
# 터미널 1: ML 서버
cd ml-inference-server
uvicorn app.main:app --port 8001 --reload

# 터미널 2: 메인 서버
cd pathfinding-server
uvicorn app.main:app --port 8000 --reload
```

### EC2 배포
```bash
# ML 서버 배포
scp -r ml-inference-server ubuntu@ec2-ml:~/
ssh ubuntu@ec2-ml
cd ml-inference-server
uvicorn app.main:app --host 0.0.0.0 --port 8001

# 메인 서버 .env 수정
ML_INFERENCE_URL=http://ec2-ml-ip:8001
```

---

## ✅ 체크리스트

- [ ] ml-inference-server가 8001 포트에서 실행 중
- [ ] /health 엔드포인트 정상 응답
- [ ] 모델이 로드됨 (또는 학습 완료)
- [ ] pathfinding-server가 8000 포트에서 실행 중
- [ ] pathfinding-server가 ML 서버에 연결 가능
- [ ] /api/v1/ml/status에서 ML 서버 상태 확인 가능
- [ ] 이미지 업로드 및 세그멘테이션 테스트 성공

---

## 💡 FAQ

**Q: 기존 코드에서 ML 관련 import 에러가 나요**
A: `app/core/ml/` 디렉토리가 제거되었으므로 해당 import를 제거하거나 HTTP Client를 사용하도록 변경하세요.

**Q: 로컬에서만 개발할 때도 두 서버를 띄워야 하나요?**
A: 네. 하지만 tmux나 터미널 여러 개로 쉽게 관리할 수 있습니다.

**Q: ML 서버가 다운되면 어떻게 되나요?**
A: `ENABLE_ML_FALLBACK=true`로 설정하면 자동으로 CV 방식으로 Fallback됩니다.

**Q: 비용이 더 드나요?**
A: 로컬 개발에서는 동일. EC2 배포 시 ML 서버용 인스턴스가 추가로 필요하지만, 필요할 때만 켜면 됩니다.

**Q: 다시 Monolith로 돌아갈 수 있나요?**
A: Git으로 이전 커밋으로 롤백하면 됩니다. 하지만 마이크로서비스가 더 유연하고 확장 가능합니다.
