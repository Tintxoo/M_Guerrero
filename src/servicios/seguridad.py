import hashlib
import hmac
import secrets


_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 600_000
_SALT_BYTES = 16
_HASH_BYTES = 32


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _ITERATIONS,
        dklen=_HASH_BYTES,
    )
    return f"{_ALGORITHM}${_ITERATIONS}${salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) == 4 and parts[0] == _ALGORITHM:
        try:
            iterations = int(parts[1])
            salt = bytes.fromhex(parts[2])
            expected_hash = bytes.fromhex(parts[3])
        except ValueError:
            return False

        if iterations <= 0 or not salt or not expected_hash:
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=len(expected_hash),
        )
        return hmac.compare_digest(actual_hash, expected_hash)

    # Legacy SHA-256 hashes are verified once and upgraded after successful login.
    if len(stored_hash) == 64:
        try:
            bytes.fromhex(stored_hash)
        except ValueError:
            return False
        legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(legacy_hash, stored_hash.lower())

    return False


def needs_rehash(stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != _ALGORITHM:
        return True

    try:
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        password_hash = bytes.fromhex(parts[3])
    except ValueError:
        return True

    return (
        iterations != _ITERATIONS
        or len(salt) != _SALT_BYTES
        or len(password_hash) != _HASH_BYTES
    )
