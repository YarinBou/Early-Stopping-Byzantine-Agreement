import hashlib
from typing import Dict

class SignatureScheme:
    def __init__(self):
        self.private: Dict[str, str] = {}
        self.public: Dict[str, str] = {}

    def keygen(self, party_id: str):
        # Simple deterministic keygen for example purposes
        priv = hashlib.sha256(f"priv:{party_id}".encode()).hexdigest()
        pub = hashlib.sha256(priv.encode()).hexdigest()
        self.private[party_id] = priv
        self.public[party_id] = pub

    def sign(self, party_id: str, message: str) -> str:
        priv = self.private[party_id]
        return hashlib.sha256((priv + message).encode()).hexdigest()

    def verify(self, party_id: str, message: str, signature: str) -> bool:
        priv = self.private.get(party_id)
        if priv is None:
            return False
        expected = hashlib.sha256((priv + message).encode()).hexdigest()
        return signature == expected
