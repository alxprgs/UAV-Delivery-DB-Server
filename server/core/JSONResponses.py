from fastapi.responses import JSONResponse
from fastapi import status

def json_success(data=None, message: str = "Success" , status_code: status = status.HTTP_200_OK):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": False,
            "message": message,
            "data": data
        }
    )

def json_error(data=None, message: str = "Error" , status_code: status = status.HTTP_500_INTERNAL_SERVER_ERROR):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": False,
            "message": message,
            "data": data
        }
    )
