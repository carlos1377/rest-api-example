from hashlib import sha256

def make_etag(payload: bytes) -> str:
    return f'W/"{sha256(payload).hexdigest()[:16]}"'
