import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
import sys

sys.path.insert(0, str(SRC))

from governed_platform.governance.file_lock import LockTimeoutError, atomic_write_json, file_lock  # noqa: E402


class FileLockTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmpdir.name) / "state.json"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_lock_timeout_when_another_writer_holds_lock(self):
        entered = threading.Event()
        release = threading.Event()

        def holder():
            with file_lock(self.state_path, timeout=1.0, poll_interval=0.01):
                entered.set()
                release.wait(timeout=2.0)

        t = threading.Thread(target=holder, daemon=True)
        t.start()
        self.assertTrue(entered.wait(timeout=1.0))

        with self.assertRaises(LockTimeoutError):
            with file_lock(self.state_path, timeout=0.1, poll_interval=0.01):
                pass

        release.set()
        t.join(timeout=2.0)

    def test_atomic_write_json_survives_concurrent_writers(self):
        def writer(worker_id: int):
            for i in range(20):
                atomic_write_json(self.state_path, {"worker": worker_id, "seq": i})

        threads = [threading.Thread(target=writer, args=(idx,), daemon=True) for idx in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        payload = json.loads(self.state_path.read_text())
        self.assertIn("worker", payload)
        self.assertIn("seq", payload)
        self.assertIsInstance(payload["worker"], int)
        self.assertIsInstance(payload["seq"], int)

    def test_stale_lock_is_recovered(self):
        lock_path = Path(f"{self.state_path}.lock")
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text("stale\n")
        stale = time.time() - 120
        os.utime(lock_path, (stale, stale))

        with file_lock(self.state_path, timeout=0.3, poll_interval=0.01, stale_after=1.0):
            self.assertTrue(lock_path.exists())
        self.assertFalse(lock_path.exists())


if __name__ == "__main__":
    unittest.main()
