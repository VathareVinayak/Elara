from fastapi import HTTPException, status

class FileTooLargeException(HTTPException):
    def __init__(self, detail="Uploaded file size exceeds limit"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UnauthorizedException(HTTPException):
    def __init__(self, detail="Unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
