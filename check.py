from typing import Dict, List
from byzantine.signatures.signature_scheme import SignatureScheme
from byzantine.signatures.proof_of_participation import PoPManager

# Parameters
n, t = 4, 1
party_ids = [f"P{i}" for i in range(n)]

# Setup
sig = SignatureScheme()
for pid in party_ids:
    sig.keygen(pid)

pops: Dict[str, Dict[str, List[str]]] = {}
managers = {}
for pid in party_ids:
    managers[pid] = PoPManager(pid, n, t, sig)

# Round 1: each sends promise
for sender in party_ids:
    msg, s = managers[sender].send_promise()
    for receiver in party_ids:
        managers[receiver].receive_promise(sender, msg, s)

# Attempt PoP generation
for pid in party_ids:
    pop = managers[pid].try_generate_pop()
    if pop:
        pops[pid] = pop
        print(f"{pid} generated PoP: {pop}")