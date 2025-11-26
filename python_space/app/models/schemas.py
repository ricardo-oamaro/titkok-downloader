from pydantic import BaseModel, HttpUrl, field_validator


class DownloadRequest(BaseModel):
    url: HttpUrl
    
    @field_validator('url')
    @classmethod
    def validate_tiktok_url(cls, v: HttpUrl) -> HttpUrl:
        url_str = str(v)
        if 'tiktok.com' not in url_str:
            raise ValueError('URL must be from tiktok.com domain')
        return v


class ErrorResponse(BaseModel):
    detail: str
    status_code: int



