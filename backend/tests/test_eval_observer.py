import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.eval_observer import EvalObserver


class MockLLMClient:
    def __init__(self, response_delay=0.01):
        self.response_delay = response_delay
        self.call_count = 0

    def generate(self, messages, timeout=None):
        self.call_count += 1
        time.sleep(self.response_delay)
        return '{"strength": "亮点", "weakness": "不足", "note": "观察"}'


class BlockingLLMClient:
    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.call_count = 0

    def generate(self, messages, timeout=None):
        self.call_count += 1
        self.started.set()
        self.release.wait(timeout=5)
        return '{"strength": "晚到结果", "weakness": "不应落库", "note": "late"}'


class MockDataClient:
    def __init__(self):
        self.save_calls = []

    def save_eval_draft(self, session_id, draft):
        self.save_calls.append((session_id, draft))
        return True


def make_history(turn: int):
    history = []
    for idx in range(1, turn + 1):
        history.extend([
            {"role": "assistant", "content": f"question-{idx}"},
            {"role": "user", "content": f"answer-{idx}"},
        ])
    return history


class EvalObserverTests(unittest.TestCase):
    def test_observe_async_updates_draft_and_pushes_callback(self):
        data_client = MockDataClient()
        observer = EvalObserver("session-1", MockLLMClient(), data_client=data_client)
        pushed = []
        observer.set_push_callback(pushed.append)

        accepted = observer.observe_async(make_history(1))

        self.assertTrue(accepted)
        draft = observer.shutdown(wait=True, timeout=1.0)
        self.assertEqual(draft["last_turn"], 1)
        self.assertEqual(len(draft["strengths"]), 1)
        self.assertEqual(len(data_client.save_calls), 1)
        self.assertEqual(len(pushed), 1)
        self.assertEqual(pushed[0]["type"], "eval_update")
        self.assertEqual(pushed[0]["turn"], 1)

    def test_duplicate_turn_is_deduplicated(self):
        observer = EvalObserver("session-2", MockLLMClient())

        first = observer.observe_async(make_history(1))
        second = observer.observe_async(make_history(1))

        self.assertTrue(first)
        self.assertFalse(second)

        draft = observer.shutdown(wait=True, timeout=1.0)
        self.assertEqual(draft["last_turn"], 1)
        self.assertEqual(len(draft["strengths"]), 1)

    def test_shutdown_waits_for_inflight_work_within_timeout(self):
        observer = EvalObserver("session-3", MockLLMClient(response_delay=0.05))

        observer.observe_async(make_history(1))
        draft = observer.shutdown(wait=True, timeout=1.0)

        self.assertEqual(draft["last_turn"], 1)
        self.assertEqual(len(draft["strengths"]), 1)

    def test_shutdown_freezes_observer_and_blocks_late_update(self):
        llm_client = BlockingLLMClient()
        data_client = MockDataClient()
        pushed = []
        observer = EvalObserver("session-4", llm_client, data_client=data_client)
        observer.set_push_callback(pushed.append)

        observer.observe_async(make_history(1))
        self.assertTrue(llm_client.started.wait(timeout=1.0))

        draft = observer.shutdown(wait=True, timeout=0.01)
        self.assertEqual(draft["last_turn"], 0)

        llm_client.release.set()
        time.sleep(0.05)

        frozen = observer.get_draft()
        self.assertEqual(frozen["last_turn"], 0)
        self.assertEqual(len(frozen["strengths"]), 0)
        self.assertEqual(len(data_client.save_calls), 0)
        self.assertEqual(len(pushed), 0)

    def test_shutdown_rejects_new_work(self):
        observer = EvalObserver("session-5", MockLLMClient())

        observer.shutdown(wait=False)
        accepted = observer.observe_async(make_history(1))

        self.assertFalse(accepted)
        self.assertEqual(observer.get_draft()["last_turn"], 0)


if __name__ == "__main__":
    unittest.main()
