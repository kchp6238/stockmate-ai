"""
관심 종목 / 즐겨찾기 API
- 서버 메모리에 저장 (재시작 시 초기화)
- 프로덕션에서는 DB(SQLite/PostgreSQL)로 교체 권장
"""
from fastapi import APIRouter, Request
from collections import defaultdict

router = APIRouter(tags=["watchlist"])

# IP별 관심 종목 저장 (서버 메모리)
_watchlists: dict[str, list[str]] = defaultdict(list)
_recents:    dict[str, list[str]] = defaultdict(list)


def _ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.get("/watchlist")
async def get_watchlist(request: Request):
    ip = _ip(request)
    return {"watchlist": _watchlists[ip], "recent": _recents[ip][-10:]}


@router.post("/watchlist/{ticker}")
async def add_watchlist(ticker: str, request: Request):
    ip = _ip(request)
    t  = ticker.upper()
    if t not in _watchlists[ip]:
        _watchlists[ip].append(t)
    return {"watchlist": _watchlists[ip]}


@router.delete("/watchlist/{ticker}")
async def remove_watchlist(ticker: str, request: Request):
    ip = _ip(request)
    t  = ticker.upper()
    _watchlists[ip] = [x for x in _watchlists[ip] if x != t]
    return {"watchlist": _watchlists[ip]}


@router.post("/recent/{ticker}")
async def add_recent(ticker: str, request: Request):
    ip = _ip(request)
    t  = ticker.upper()
    lst = _recents[ip]
    if t in lst:
        lst.remove(t)
    lst.insert(0, t)
    _recents[ip] = lst[:10]  # 최근 10개만
    return {"recent": _recents[ip]}
