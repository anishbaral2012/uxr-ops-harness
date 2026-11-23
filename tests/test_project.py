import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from uxrops.project import ProjectError, compute_status, load_project, record  # noqa: E402
from uxrops.scaffold import init_study  # noqa: E402

UXROPS = ROOT / "scripts" / "uxrops.py"


class ProjectStatusTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "brief.md").write_text("brief", encoding="utf-8")
        (self.root / "plan.md").write_text("plan", encoding="utf-8")
        (self.root / "transcripts").mkdir()
        (self.root / "transcripts" / "p1.txt").write_text("source", encoding="utf-8")
        (self.root / "analysis.md").write_text("analysis", encoding="utf-8")
        self.project = self.root / "uxr-project.json"
        self.write({
            "brief": {"paths": ["brief.md"], "inputs": []},
            "plan": {"paths": ["plan.md"], "inputs": ["brief"]},
            "sources": {"paths": ["transcripts/"], "inputs": []},
            "analysis": {"paths": ["analysis.md"], "inputs": ["plan", "sources"]},
            "deck": {"paths": ["deck.pptx"], "inputs": ["analysis"], "status": "planned"},
        })

    def write(self, artifacts):
        self.project.write_text(json.dumps({"artifacts": artifacts}), encoding="utf-8")

    def states(self):
        path, data = load_project(self.root)
        return {r["artifact"]: r["state"] for r in compute_status(path, data)[0]}

    def record_all(self, *ids):
        for aid in ids:
            path, data = load_project(self.root)
            record(path, data, aid, status="reviewed")

    def test_unrecorded_then_ok(self):
        self.assertEqual(self.states()["plan"], "unrecorded")
        self.assertEqual(self.states()["deck"], "planned")
        self.record_all("brief", "plan", "sources", "analysis")
        self.assertEqual(set(self.states().values()), {"ok", "planned"})

    def test_upstream_change_propagates(self):
        self.record_all("brief", "plan", "sources", "analysis")
        (self.root / "brief.md").write_text("brief v2", encoding="utf-8")
        states = self.states()
        self.assertEqual(states["brief"], "modified")
        self.assertEqual(states["plan"], "stale")
        self.assertEqual(states["analysis"], "stale")

    def test_new_source_file_makes_analysis_stale(self):
        self.record_all("brief", "plan", "sources", "analysis")
        (self.root / "transcripts" / "p2.txt").write_text("new", encoding="utf-8")
        self.assertEqual(self.states()["sources"], "modified")
        self.assertEqual(self.states()["analysis"], "stale")

    def test_rerecording_upstream_still_flags_downstream(self):
        self.record_all("brief", "plan", "sources", "analysis")
        (self.root / "plan.md").write_text("plan v2", encoding="utf-8")
        self.record_all("plan")
        self.assertEqual(self.states()["plan"], "ok")
        self.assertEqual(self.states()["analysis"], "stale")

    def test_record_refuses_stale_inputs(self):
        self.record_all("brief", "plan", "sources")
        (self.root / "brief.md").write_text("changed", encoding="utf-8")
        path, data = load_project(self.root)
        with self.assertRaisesRegex(ProjectError, "inputs are not ok"):
            record(path, data, "analysis")
        record(path, data, "analysis", allow_stale_inputs=True)

    def test_missing_file_and_cycle_and_escape(self):
        self.record_all("brief", "plan")
        (self.root / "plan.md").unlink()
        self.assertEqual(self.states()["plan"], "missing")
        self.write({"a": {"paths": [], "inputs": ["b"]}, "b": {"paths": [], "inputs": ["a"]}})
        with self.assertRaisesRegex(ProjectError, "cycle"):
            load_project(self.root)
        self.write({"a": {"paths": ["../outside.txt"], "inputs": []}})
        path, data = load_project(self.root)
        with self.assertRaisesRegex(ProjectError, "inside the study folder"):
            compute_status(path, data)

    def test_record_writes_atomically(self):
        self.record_all("brief")
        self.assertEqual([p.name for p in self.root.glob(".uxr-project.json.*")], [])
        data = json.loads(self.project.read_text(encoding="utf-8"))
        self.assertIn("files", data["artifacts"]["brief"]["recorded"])

    def test_cli_status_exit_codes_and_mark_stale(self):
        run = lambda *a: subprocess.run([sys.executable, str(UXROPS), *a], capture_output=True, text=True, check=False)
        self.assertEqual(run("status", str(self.root)).returncode, 1)
        for aid in ("brief", "plan", "sources", "analysis"):
            self.assertEqual(run("record", aid, "--project", str(self.root), "--status", "reviewed").returncode, 0)
        self.assertEqual(run("status", str(self.root)).returncode, 0)
        (self.root / "plan.md").write_text("plan v2", encoding="utf-8")
        result = run("status", str(self.root), "--mark-stale", "--format", "json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["marked_stale"], ["plan", "analysis"])
        data = json.loads(self.project.read_text(encoding="utf-8"))
        self.assertEqual(data["artifacts"]["analysis"]["status"], "stale")


class InitTests(unittest.TestCase):
    def test_init_creates_skeleton_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "study"
            folder.mkdir()
            (folder / "study-manifest.json").write_text("keep me", encoding="utf-8")
            created, skipped = init_study(folder, study="Demo")
            self.assertIn("uxr-project.json", created)
            self.assertEqual(skipped, ["study-manifest.json"])
            self.assertEqual((folder / "study-manifest.json").read_text(encoding="utf-8"), "keep me")
            self.assertIn("* -text", (folder / ".gitattributes").read_text(encoding="utf-8"))
            self.assertTrue((folder / "transcripts").is_dir())
            path, data = load_project(folder)
            self.assertEqual(data["study"], "Demo")
            states = {r["state"] for r in compute_status(path, data)[0]}
            self.assertEqual(states, {"planned", "unrecorded"})


class FixtureTests(unittest.TestCase):
    """The committed fixture must verify after checkout on every OS (line-ending safety)."""

    FIXTURE = ROOT / "tests" / "fixtures" / "mini-study"

    def test_fixture_hashes_survive_checkout(self):
        result = subprocess.run([sys.executable, str(UXROPS), "verify", str(self.FIXTURE)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout)

    @unittest.skipIf(shutil.which("git") is None, "git is not installed")
    def test_study_files_are_not_line_ending_converted(self):
        probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT,
                               capture_output=True, text=True, check=False)
        if probe.stdout.strip() != "true":
            self.skipTest("not a git checkout")
        paths = ["tests/fixtures/mini-study/transcripts/S1-P1.txt", "studies/x/transcripts/a.txt",
                 "studies/x/analysis.md", "elsewhere/study/transcripts/a.txt"]
        result = subprocess.run(["git", "check-attr", "text", "--", *paths], cwd=ROOT,
                                capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            self.assertTrue(line.endswith(": text: unset"), line)


if __name__ == "__main__":
    unittest.main()
