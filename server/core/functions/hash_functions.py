import hashlib

def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def verify_sha256(text: str, expected_hash: str) -> bool:   
    computed_hash = sha256_hash(text)
    return computed_hash.lower() == expected_hash.lower()