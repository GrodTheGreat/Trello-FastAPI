from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return hasher.hash(password)


def is_correct_password(password: str, password_hash: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False
