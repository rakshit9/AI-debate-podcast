import uuid

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def generate_api_key() -> tuple[str, str]:
    """Return (raw_key, hashed_key). Raw key shown once; only hash stored."""
    raw = f"pfk_{uuid.uuid4().hex}"
    return raw, _pwd_context.hash(raw)
