"""
StockAI - FastAPI 백엔드 진입점
실행: uvicorn main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from limiter import limiter
from routers import stock, analysis, news, watchlist, recommend

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 StockAI 서버 시작")
    yield
    logger.info("🛑 서버 종료")


app = FastAPI(
    title="StockAI API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 미들웨어
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


# 전역 예외 처리
@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.error(f"처리되지 않은 예외: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "서버 내부 오류입니다. 잠시 후 다시 시도해 주세요."})


# 라우터 등록
app.include_router(stock.router,     prefix="/api")
app.include_router(analysis.router,  prefix="/api")
app.include_router(news.router,      prefix="/api")
app.include_router(watchlist.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}
