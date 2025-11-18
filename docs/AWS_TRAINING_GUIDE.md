# AWS 클라우드 학습 가이드

## 📋 개요

M1 Mac에서 학습이 느리거나 리소스가 부족한 경우 AWS에서 학습하는 방법입니다.

## 🚀 방법 1: AWS EC2 GPU 인스턴스 (추천)

### 💰 비용 효율적인 인스턴스 추천

| 인스턴스 타입 | GPU | vCPU | 메모리 | 시간당 비용 | 추천 용도 |
|--------------|-----|------|--------|------------|----------|
| **g4dn.xlarge** | NVIDIA T4 (16GB) | 4 | 16GB | $0.526 | 가장 저렴, 테스트 |
| **g4dn.2xlarge** | NVIDIA T4 (16GB) | 8 | 32GB | $0.752 | **추천**, 균형 |
| **g5.xlarge** | NVIDIA A10G (24GB) | 4 | 16GB | $1.006 | 빠른 학습 |
| **p3.2xlarge** | NVIDIA V100 (16GB) | 8 | 61GB | $3.06 | 최고 성능 |

**추천**: `g4dn.2xlarge` - 성능과 가격 균형이 좋음

### 1️⃣ EC2 인스턴스 시작

#### AWS 콘솔에서 설정

```bash
# 1. AWS Management Console 접속
# 2. EC2 → Launch Instance
# 3. 설정:
#    - Name: ml-training-instance
#    - AMI: Deep Learning AMI GPU PyTorch (Ubuntu 20.04)
#    - Instance type: g4dn.2xlarge
#    - Key pair: 새로 생성 또는 기존 사용
#    - Storage: 100GB gp3
#    - Security Group: SSH (22), Custom TCP (8888 for Jupyter)
```

#### AWS CLI로 빠른 시작

```bash
# AWS CLI 설치 및 설정
aws configure

# 키페어 생성 (최초 1회)
aws ec2 create-key-pair \
  --key-name ml-training-key \
  --query 'KeyMaterial' \
  --output text > ml-training-key.pem

chmod 400 ml-training-key.pem

# Deep Learning AMI ID 확인 (us-east-1 기준)
# AMI ID는 리전별로 다르므로 AWS 콘솔에서 확인 필요
AMI_ID="ami-0c7217cdde317cfec"  # Deep Learning AMI GPU PyTorch 2.0

# EC2 인스턴스 시작
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type g4dn.2xlarge \
  --key-name ml-training-key \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ml-training}]'
```

### 2️⃣ 인스턴스 접속 및 환경 설정

```bash
# 인스턴스 Public IP 확인
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=ml-training" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# SSH 접속 (IP 주소는 위에서 확인한 것으로 대체)
ssh -i ml-training-key.pem ubuntu@<YOUR_INSTANCE_IP>
```

### 3️⃣ 프로젝트 업로드 및 학습

```bash
# === 로컬에서 실행 (프로젝트 압축) ===
cd /Users/ktg/Desktop/load_generate_ai
tar -czf pathfinding-server.tar.gz pathfinding-server/

# 서버로 업로드
scp -i ml-training-key.pem pathfinding-server.tar.gz ubuntu@<YOUR_INSTANCE_IP>:~/

# === EC2 인스턴스에서 실행 ===
# SSH 접속 후

# 압축 해제
tar -xzf pathfinding-server.tar.gz
cd pathfinding-server

# 가상환경 생성 (Deep Learning AMI는 conda 제공)
conda create -n pathfinding python=3.10 -y
conda activate pathfinding

# 의존성 설치
pip install -r requirements_ml.txt

# GPU 확인
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"

# 학습 시작 (GPU 사용)
python -m app.core.ml.train \
  --generate_data \
  --epochs 50 \
  --batch_size 32 \
  --use_wandb

# 또는 백그라운드 실행 (SSH 연결 끊어도 계속 실행)
nohup python -m app.core.ml.train \
  --generate_data \
  --epochs 50 \
  --batch_size 32 \
  --use_wandb > training.log 2>&1 &

# 로그 확인
tail -f training.log
```

### 4️⃣ 학습 모니터링

#### TensorBoard 원격 접속

```bash
# === EC2 인스턴스에서 ===
tensorboard --logdir logs --host 0.0.0.0 --port 6006 &

# === 로컬 컴퓨터에서 ===
# SSH 터널링
ssh -i ml-training-key.pem -L 6006:localhost:6006 ubuntu@<YOUR_INSTANCE_IP>

# 브라우저에서 접속
# http://localhost:6006
```

#### Weights & Biases 사용 (추천)

```bash
# EC2에서 한 번만 설정
wandb login  # API key 입력

# 학습 시 --use_wandb 플래그 사용
python -m app.core.ml.train --generate_data --epochs 50 --use_wandb

# wandb.ai 웹사이트에서 실시간 모니터링 가능
```

### 5️⃣ 학습 완료 후 모델 다운로드

```bash
# === EC2 인스턴스에서 ===
# 모델 압축
cd ~/pathfinding-server
tar -czf trained_models.tar.gz models/ logs/

# === 로컬 컴퓨터에서 ===
# 모델 다운로드
scp -i ml-training-key.pem ubuntu@<YOUR_INSTANCE_IP>:~/pathfinding-server/trained_models.tar.gz .

# 압축 해제
tar -xzf trained_models.tar.gz

# 원래 프로젝트에 복사
cp -r models/* /Users/ktg/Desktop/load_generate_ai/pathfinding-server/models/
cp -r logs/* /Users/ktg/Desktop/load_generate_ai/pathfinding-server/logs/
```

### 6️⃣ 인스턴스 종료 (중요!)

```bash
# 학습 완료 후 반드시 인스턴스 종료하여 비용 절약
aws ec2 stop-instances --instance-ids <INSTANCE_ID>

# 또는 완전히 삭제
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>
```

---

## 🚀 방법 2: AWS SageMaker (관리형 서비스)

### 장점
- 자동 환경 설정
- Jupyter Notebook 제공
- 자동 인스턴스 관리
- 실험 추적 기능

### 단점
- EC2보다 약간 비쌈
- 초기 설정이 복잡

### 1️⃣ SageMaker 노트북 인스턴스 생성

```bash
# AWS CLI로 생성
aws sagemaker create-notebook-instance \
  --notebook-instance-name ml-training-notebook \
  --instance-type ml.g4dn.2xlarge \
  --role-arn arn:aws:iam::<YOUR_ACCOUNT_ID>:role/SageMakerRole \
  --volume-size-in-gb 100

# 상태 확인
aws sagemaker describe-notebook-instance \
  --notebook-instance-name ml-training-notebook
```

### 2️⃣ Jupyter Notebook에서 학습

```python
# SageMaker Notebook에서 실행

# 프로젝트 클론 또는 업로드
!git clone <YOUR_REPO_URL>
# 또는 파일 업로드

cd pathfinding-server

# 의존성 설치
!pip install -r requirements_ml.txt

# 학습 실행
!python -m app.core.ml.train \
  --generate_data \
  --epochs 50 \
  --batch_size 32 \
  --use_wandb
```

### 3️⃣ SageMaker Training Job 사용 (프로덕션)

학습 스크립트를 SageMaker Training Job으로 실행하면:
- 자동 스케일링
- 분산 학습 지원
- S3 통합

```python
# sagemaker_training.py 예제
import sagemaker
from sagemaker.pytorch import PyTorch

# SageMaker Session
session = sagemaker.Session()
role = sagemaker.get_execution_role()

# PyTorch Estimator 생성
estimator = PyTorch(
    entry_point='app/core/ml/train.py',
    source_dir='.',
    role=role,
    framework_version='2.0',
    py_version='py310',
    instance_count=1,
    instance_type='ml.g4dn.2xlarge',
    hyperparameters={
        'epochs': 50,
        'batch_size': 32,
        'lr': 0.001,
        'generate_data': True
    },
    output_path='s3://your-bucket/models',
    base_job_name='map-segmentation'
)

# 학습 시작
estimator.fit()
```

---

## 💡 비용 절약 팁

### 1. Spot Instances 사용 (최대 90% 할인)

```bash
# EC2 Spot Instance 요청
aws ec2 request-spot-instances \
  --spot-price "0.3" \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification '{
    "ImageId": "ami-0c7217cdde317cfec",
    "InstanceType": "g4dn.2xlarge",
    "KeyName": "ml-training-key",
    "BlockDeviceMappings": [{
      "DeviceName": "/dev/sda1",
      "Ebs": {"VolumeSize": 100, "VolumeType": "gp3"}
    }]
  }'
```

**주의**: Spot Instance는 중단될 수 있으므로 체크포인트 저장 필수

### 2. 학습 완료 후 자동 종료

```bash
# EC2 인스턴스에서 학습 스크립트 끝에 추가
python -m app.core.ml.train --generate_data --epochs 50

# 학습 완료 후 자동 종료
sudo shutdown -h now
```

### 3. 예상 비용 계산

| 학습 시나리오 | 인스턴스 | 예상 시간 | 비용 |
|--------------|---------|----------|------|
| 50 epochs, batch 16 | g4dn.2xlarge | ~3시간 | $2.25 |
| 100 epochs, batch 32 | g4dn.2xlarge | ~5시간 | $3.76 |
| 50 epochs, batch 32 | g5.xlarge | ~2시간 | $2.01 |

---

## 🔧 트러블슈팅

### GPU 인식 안될 때

```bash
# NVIDIA 드라이버 확인
nvidia-smi

# CUDA 버전 확인
nvcc --version

# PyTorch CUDA 확인
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory 에러

```python
# train.py에서 batch_size 줄이기
python -m app.core.ml.train \
  --generate_data \
  --epochs 50 \
  --batch_size 8  # 32 → 8
```

### SSH 연결 끊김

```bash
# tmux 사용 (세션 유지)
tmux new -s training

# 학습 실행
python -m app.core.ml.train --generate_data --epochs 50

# Ctrl+B, D로 detach
# 나중에 재접속
tmux attach -t training
```

---

## 📊 성능 비교

| 환경 | GPU | 배치 크기 | Epoch당 시간 | 50 Epochs 총 시간 |
|-----|-----|----------|------------|-----------------|
| **M1 Mac** | Apple Silicon | 8 | ~8분 | ~6.5시간 |
| **EC2 g4dn.2xlarge** | NVIDIA T4 | 32 | ~2분 | ~1.7시간 |
| **EC2 g5.xlarge** | NVIDIA A10G | 32 | ~1.5분 | ~1.2시간 |
| **EC2 p3.2xlarge** | NVIDIA V100 | 32 | ~1분 | ~50분 |

---

## ✅ 권장 워크플로우

1. **로컬 (M1)**: 소규모 테스트 (5 epochs, 작은 데이터셋)
2. **AWS EC2 g4dn.2xlarge**: 전체 학습 (50-100 epochs)
3. **결과 다운로드**: 모델을 로컬로 가져와서 사용

```bash
# 로컬 테스트
python -m app.core.ml.train --generate_data --epochs 5 --batch_size 4

# AWS에서 전체 학습
# (위 가이드 참고)

# 모델 다운로드 후 로컬에서 사용
python -m app.core.ml.train --model_path models/best_model.pth
```
