import uuid

import bcrypt


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_api_key() -> tuple[str, str]:
    """Return (raw_key, hashed_key). Raw key shown once; only hash stored."""
    raw = f"pfk_{uuid.uuid4().hex}"
    return raw, hash_password(raw)
