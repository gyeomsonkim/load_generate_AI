"""
API 사용량 추적 미들웨어
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from typing import Callable

from app.models.database import ApiKey, ApiUsage
from app.api.dependencies import get_async_session

logger = logging.getLogger(__name__)


class ApiUsageTrackerMiddleware(BaseHTTPMiddleware):
    """
    모든 API 요청의 사용량을 추적하는 미들웨어

    - 응답 시간 측정
    - API 키별 사용량 기록
    - 엔드포인트, 메서드, 상태 코드 저장
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # 시작 시간 기록
        start_time = time.time()

        # API 키 추출
        api_key_value = request.headers.get("X-API-Key")

        # 요청 처리
        response = await call_next(request)

        # 응답 시간 계산 (밀리초)
        response_time_ms = (time.time() - start_time) * 1000

        # API 키가 있으면 사용량 기록
        if api_key_value:
            try:
                await self._log_api_usage(
                    api_key_value=api_key_value,
                    endpoint=str(request.url.path),
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    user_agent=request.headers.get("User-Agent")
                )
            except Exception as e:
                # 사용량 기록 실패해도 응답은 정상 반환
                logger.error(f"API 사용량 기록 실패: {e}", exc_info=True)

        return response

    async def _log_api_usage(
        self,
        api_key_value: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_agent: str = None
    ):
        """
        API 사용량을 데이터베이스에 기록

        Args:
            api_key_value: API 키 값
            endpoint: 엔드포인트 경로
            method: HTTP 메서드
            status_code: 응답 상태 코드
            response_time_ms: 응답 시간 (밀리초)
            user_agent: User-Agent 헤더
        """
        try:
            # 비동기 세션 생성
            async for db in get_async_session():
                # API 키 조회
                result = await db.execute(
                    select(ApiKey).where(ApiKey.key == api_key_value)
                )
                api_key = result.scalar_one_or_none()

                if not api_key:
                    logger.warning(f"Unknown API key: {api_key_value}")
                    return

                # 사용량 카운트 증가
                api_key.usage_count += 1

                # 사용량 기록 생성
                api_usage = ApiUsage(
                    api_key_id=api_key.id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    response_time_ms=round(response_time_ms, 2),
                    user_agent=user_agent
                )
                db.add(api_usage)

                await db.commit()

                logger.debug(
                    f"API usage logged: {method} {endpoint} "
                    f"[{status_code}] {response_time_ms:.2f}ms"
                )
                break

        except Exception as e:
            logger.error(f"사용량 기록 저장 실패: {e}", exc_info=True)
