from fastapi import Depends, HTTPException, Request, status
from app.security.auth import require_api_key

async def admin_only(request: Request, _=Depends(require_api_key())):
    if not getattr(request.state, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
