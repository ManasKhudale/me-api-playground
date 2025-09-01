import os, time
from fastapi import Request, HTTPException

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
BUCKET = {}

def rate_limit(request: Request):
    # naive per-IP fixed window
    ip = request.client.host if request.client else "unknown"
    now = int(time.time() // 60)  # current minute
    key = f"{ip}:{now}"
    count = BUCKET.get(key, 0) + 1
    BUCKET[key] = count
    if count > RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
