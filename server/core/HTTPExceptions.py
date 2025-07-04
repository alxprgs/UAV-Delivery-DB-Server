from fastapi import HTTPException, status

def http_unauthorized(detail="Unauthorized"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

def http_forbidden(detail="Forbidden"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

def http_not_found(detail="Not Found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def http_bad_request(detail="Bad Request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

def http_conflict(detail="Conflict"):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
