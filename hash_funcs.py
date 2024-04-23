import hashlib


def get_hash_of_file(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()
