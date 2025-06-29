from typing import Dict, Callable

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from server.core.functions.db_functions import check_user

bearer_scheme = HTTPBearer(bearerFormat="JWT", scheme_name="JWT")
custom_header_scheme = APIKeyHeader(name="JWT_TOKEN", auto_error=False)


async def get_current_user(
    bearer: HTTPAuthorizationCredentials = Security(bearer_scheme),
    custom: str | None = Security(custom_header_scheme),
):
    token = bearer.credentials if bearer else custom
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing credentials")

    ok, user = await check_user(token)
    if not ok:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token")
    return user

def require_access(permission: str) -> Callable:
    async def checker(user: Dict = Depends(get_current_user)) -> Dict:
        access = user.get("access", {})
        if access.get("all") or access.get(permission):
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"No {permission} permission")
    return checker