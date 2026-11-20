import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_study.py"
spec = importlib.util.spec_from_file_location("verify_study", SCRIPT)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class StudyVerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "p1.txt"
        self.source.write_text("First session: a real quote.", encoding="utf-8")
        self.followup = self.root / "p1-followup.txt"
        self.followup.write_text("Follow-up: another observation.", encoding="utf-8")
        sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        followup_sha = hashlib.sha256(self.followup.read_bytes()).hexdigest()
        self.manifest = {
            "participants": ["P1", "P2"],
            "sources": [
                {"id": "S1", "participant_id": "P1", "session_id": "A", "path": "p1.txt", "sha256": sha},
                {"id": "S2", "participant_id": "P1", "session_id": "B", "path": "p1-followup.txt", "sha256": followup_sha},
            ],
        }
        self.ledger = {
            "source_snapshot": {"S1": sha, "S2": followup_sha},
            "themes": [
                {"id": "T1", "claim": "An observation", "supporting_participants": ["P1"],
                 "counter_evidence": "Searched both accounts; none found.",
                 "evidence": [
                     {"source_id": "S1", "source_sha256": sha, "locator": "line 1",
                      "polarity": "support", "quote": "a real quote"},
                     {"source_id": "S2", "source_sha256": followup_sha, "locator": "line 1",
                      "polarity": "support", "quote": "another observation"},
                 ]}
            ]
        }
        self.manifest_path = self.root / "manifest.json"
        self.ledger_path = self.root / "ledger.json"

    def check(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")
        self.ledger_path.write_text(json.dumps(self.ledger), encoding="utf-8")
        return verifier.verify(self.manifest_path, self.ledger_path)

    def test_multiple_sources_are_one_participant(self):
        self.assertEqual(self.check(), [])

    def test_cli_accepts_valid_ledger(self):
        self.check()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify", str(self.manifest_path), str(self.ledger_path)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("researcher review remains required", result.stdout)

    def test_replaced_source_detected_even_if_file_count_is_unchanged(self):
        self.source.write_text("First session: a different quote.", encoding="utf-8")
        result = " ".join(self.check())
        self.assertIn("source hash drift", result)
        self.assertIn("evidence source hash drift", result)
        self.assertIn("excerpt not found", result)

    def test_updating_manifest_hash_does_not_hide_stale_ledger(self):
        self.source.write_text("First session: a real quote. Changed.", encoding="utf-8")
        self.manifest["sources"][0]["sha256"] = verifier.digest(self.source)
        result = " ".join(self.check())
        self.assertIn("evidence source hash drift", result)

    def test_manifest_source_set_changes_invalidate_snapshot(self):
        self.manifest["sources"].pop()
        result = " ".join(self.check())
        self.assertIn("source snapshot IDs differ", result)
        self.manifest["sources"].append(
            {"id": "S3", "participant_id": "P1", "session_id": "B",
             "path": "p1-followup.txt", "sha256": verifier.digest(self.followup)}
        )
        self.assertIn("source snapshot IDs differ", " ".join(self.check()))

    def test_incorrect_attribution_or_participant_count_fails(self):
        self.ledger["themes"][0]["supporting_participants"] = ["P1", "P2"]
        self.assertIn("supporting participant IDs do not match", " ".join(self.check()))
        self.ledger["themes"][0]["evidence"][0]["source_id"] = "missing"
        self.assertIn("unknown source", " ".join(self.check()))

    def test_duplicate_paths_and_outside_paths_fail(self):
        self.manifest["sources"][1]["path"] = "p1.txt"
        self.assertIn("duplicate source path", " ".join(self.check()))
        self.manifest["sources"][1]["path"] = "../outside.txt"
        self.assertIn("must stay inside", " ".join(self.check()))

    def test_missing_counter_evidence_and_quote_fail(self):
        self.ledger["themes"][0]["counter_evidence"] = ""
        self.ledger["themes"][0]["evidence"][0]["quote"] = "invented"
        result = " ".join(self.check())
        self.assertIn("missing counter_evidence", result)
        self.assertIn("excerpt not found", result)

    def test_no_research_sources_cannot_pass(self):
        self.manifest["sources"] = []
        self.ledger = {"source_snapshot": {}, "themes": []}
        self.assertIn("At least one research source", " ".join(self.check()))

    def test_bad_json_and_cli_exit_status(self):
        self.check()
        self.ledger_path.write_text("{", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify", str(self.manifest_path), str(self.ledger_path)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Cannot read JSON", result.stdout)


if __name__ == "__main__":
    unittest.main()
