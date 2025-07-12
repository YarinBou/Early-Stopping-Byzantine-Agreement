import unittest
from byzantine.signatures.signature_scheme import SignatureScheme
from byzantine.signatures.proof_of_participation import PoPManager, PoPData

class TestPoPManager(unittest.TestCase):
    def setUp(self):
        self.n = 4
        self.t = 1
        self.party_ids = [f"P{i}" for i in range(self.n)]

        # Initialize shared signature scheme
        self.sig = SignatureScheme()
        for pid in self.party_ids:
            self.sig.keygen(pid)

        # Create a PoPManager for each party
        self.managers = {
            pid: PoPManager(pid, self.n, self.t, self.sig)
            for pid in self.party_ids
        }

    def test_honest_pop_generation(self):
        """
        All parties honestly send and receive promises.
        Everyone should be able to generate a valid PoP.
        """
        # Round 1: everyone sends their promise to everyone
        for sender in self.party_ids:
            msg, signature = self.managers[sender].send_promise()
            for receiver in self.party_ids:
                self.managers[receiver].receive_promise(sender, sender, signature)

        # Now each party should be able to generate and verify its own PoP
        for pid in self.party_ids:
            pop = self.managers[pid].try_generate_pop()
            self.assertIsNotNone(pop, f"{pid} failed to generate PoP")
            self.assertTrue(
                PoPManager.verify_pop(pop, self.sig, self.t),
                f"Verification failed for {pid}'s PoP"
            )

    def test_insufficient_promises_no_pop(self):
        """
        Only one promise received—not enough to reach threshold.
        """
        pid = self.party_ids[0]
        mgr = self.managers[pid]

        # Only self sends
        msg, signature = mgr.send_promise()
        mgr.receive_promise(pid, pid, signature)

        pop = mgr.try_generate_pop()
        self.assertIsNone(pop, "PoP should not be generated with only one promise")

    def test_invalid_signature_rejected(self):
        """
        Manager should ignore invalid signatures.
        """
        target = self.party_ids[0]
        mgr = self.managers[target]

        # Add a valid promise from P1
        msg1, sig1 = self.managers["P1"].send_promise()
        mgr.receive_promise("P1", target, sig1)

        # Add an invalid/corrupt promise from P2
        mgr.receive_promise("P2", target, "bad_signature")

        # Should not have enough valid signatures yet
        pop = mgr.try_generate_pop()
        self.assertIsNone(pop, "PoP should not generate with invalid signatures")

        # Add a second valid promise to reach threshold
        msg3, sig3 = self.managers["P3"].send_promise()
        mgr.receive_promise("P3", target, sig3)

        pop = mgr.try_generate_pop()
        self.assertIsNotNone(pop, "PoP should now generate with 2 valid promises")
        self.assertTrue(
            PoPManager.verify_pop(pop, self.sig, self.t),
            "Generated PoP failed verification"
        )

if __name__ == "__main__":
    unittest.main()
