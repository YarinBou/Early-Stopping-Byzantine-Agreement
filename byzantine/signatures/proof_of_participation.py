import hashlib
from typing import Optional, Dict, List, TypedDict
from .signature_scheme import SignatureScheme

class PoPData(TypedDict):
    msg: str
    signatures: List[str]
    signers: List[str]

class PoPManager:
    def __init__(self, party_id: str, n: int, t: int, sig: SignatureScheme):
        self.party_id = party_id
        self.n = n
        self.t = t
        self.sig = sig
        # Tracks: owner_id → { sender_id → signature }
        self.promises: Dict[str, Dict[str, str]] = {}

    def receive_promise(self, sender_id: str, owner_id: str, signature: str) -> None:
        """
        Receives a promise message from sender_id about owner_id's participation.
        """
        msg = f"promise:{owner_id}"
        if self.sig.verify(sender_id, msg, signature):
            if owner_id not in self.promises:
                self.promises[owner_id] = {}
            self.promises[owner_id][sender_id] = signature

    def send_promise(self) -> tuple[str, str]:
        """
        Generates the promise message and its signature to send to others.
        """
        msg = f"promise:{self.party_id}"
        signature = self.sig.sign(self.party_id, msg)
        return msg, signature

    def try_generate_pop(self) -> Optional[PoPData]:
        """
        Attempts to generate a PoP for self.party_id if enough valid promises are collected.
        Returns PoPData if successful, else None.
        """
        sigs_by = self.promises.get(self.party_id, {})
        if len(sigs_by) >= self.t + 1:
            selected_signers = list(sigs_by.keys())[: self.t + 1]
            selected_sigs = [sigs_by[s] for s in selected_signers]
            return PoPData(
                msg=f"promise:{self.party_id}",
                signatures=selected_sigs,
                signers=selected_signers
            )
        return None

    @staticmethod
    def verify_pop(pop: PoPData, sig: SignatureScheme, t: int) -> bool:
        """
        Verifies that a given PoPData object is valid:
        - msg has correct format
        - At least t+1 valid signatures from distinct signers
        """
        msg = pop["msg"]
        sigs = pop["signatures"]
        signers = pop["signers"]

        if len(sigs) < t + 1 or len(signers) != len(sigs):
            return False
        if not msg.startswith("promise:"):
            return False

        for signer, signature in zip(signers, sigs):
            if not sig.verify(signer, msg, signature):
                return False

        return True
