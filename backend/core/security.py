from datetime import timedelta


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    raise NotImplementedError


def decode_token(token: str) -> dict:
    raise NotImplementedError
