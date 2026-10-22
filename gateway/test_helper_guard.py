"""Provider/helper failures must return the device to standby."""
import asyncio
import unittest
from types import SimpleNamespace

from server import XiaozhiSession


def make_session(*, ready=False):
    session = XiaozhiSession.__new__(XiaozhiSession)
    session.helper_guard = None
    session.process_watch_task = None
    session.helper_ready = asyncio.Event()
    if ready:
        session.helper_ready.set()
    session.transcript_final_at = 0.0
    session.input_stopped = False
    session.tag = "[test]"
    session.HELPER_START_TIMEOUT_SECONDS = 0.02
    session.LISTENING_NO_TRANSCRIPT_SECONDS = 0.02
    session.process = SimpleNamespace(returncode=None)
    reasons = []

    async def return_to_standby(reason):
        reasons.append(reason)
        session.input_stopped = True

    session.return_to_standby = return_to_standby
    return session, reasons


class HelperGuardBehaviour(unittest.IsolatedAsyncioTestCase):
    async def test_start_timeout_recycles_connection(self):
        session, reasons = make_session()
        session.arm_helper_guard(session.process)
        await asyncio.wait_for(session.helper_guard, timeout=1)
        self.assertEqual(reasons, ["helper_start_timeout"])

    async def test_no_transcript_recycles_connection(self):
        session, reasons = make_session(ready=True)
        session.arm_helper_guard(session.process)
        await asyncio.wait_for(session.helper_guard, timeout=1)
        self.assertEqual(reasons, ["no_transcript_timeout"])

    async def test_final_transcript_keeps_connection(self):
        session, reasons = make_session(ready=True)
        session.transcript_final_at = 1.0
        session.arm_helper_guard(session.process)
        await asyncio.wait_for(session.helper_guard, timeout=1)
        self.assertEqual(reasons, [])


if __name__ == "__main__":
    unittest.main()
