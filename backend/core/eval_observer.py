"""
EvalObserver - real-time interview evaluation observer.

After each turn, a background task can:
1. Ask a secondary LLM for a concise turn-level assessment
2. Update the in-memory draft
3. Sync the draft to the data service

The main interview flow should never block on these tasks, but shutdown must be
predictable: once an interview is ending, no late draft writes should appear.
"""

import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, wait as wait_futures
from typing import Dict, List, Optional, Set


class EvalObserver:
    def __init__(self, session_id: str, llm_client, data_client=None):
        self.session_id = session_id
        self.llm_client = llm_client
        self.data_client = data_client
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._accepting = True
        self._shutdown = False
        self._push_callback = None
        self._futures: Set = set()
        self._pending_turns: Set[int] = set()
        self.draft: Dict = {
            "strengths": [],
            "weaknesses": [],
            "turn_notes": [],
            "last_turn": 0,
        }

    def set_push_callback(self, callback):
        """Register the SSE push callback."""
        with self._lock:
            self._push_callback = callback

    def observe_async(self, chat_history: List[Dict]) -> bool:
        """Submit a turn evaluation task if this observer is still accepting work."""
        turn = len(chat_history) // 2
        with self._lock:
            if self._shutdown or not self._accepting:
                return False
            if turn <= 0 or turn <= self.draft["last_turn"] or turn in self._pending_turns:
                return False
            self._pending_turns.add(turn)

        try:
            future = self._executor.submit(self._observe_safe, turn, list(chat_history))
        except RuntimeError:
            with self._lock:
                self._pending_turns.discard(turn)
            return False

        with self._lock:
            self._futures.add(future)
        future.add_done_callback(self._on_future_done)
        return True

    def _on_future_done(self, future) -> None:
        with self._lock:
            self._futures.discard(future)

    def _observe_safe(self, turn: int, chat_history: List[Dict]) -> None:
        if self._shutdown:
            with self._lock:
                self._pending_turns.discard(turn)
            return
        try:
            self._observe(turn, chat_history)
        except Exception as e:
            print(f"[EvalObserver] 未捕获异常：{e}")
        finally:
            with self._lock:
                self._pending_turns.discard(turn)

    def _observe(self, turn: int, chat_history: List[Dict]) -> None:
        with self._lock:
            if self._shutdown or turn <= self.draft["last_turn"]:
                return

        last_q, last_a = "", ""
        for message in reversed(chat_history):
            if not last_a and message["role"] == "user":
                last_a = message["content"][:400]
            elif not last_q and message["role"] == "assistant":
                last_q = message["content"][:300]
            if last_q and last_a:
                break

        if not last_a:
            return

        prompt = (
            "你是面试评估观察员，只分析本轮对话片段，输出简洁 JSON。\n\n"
            f"面试官问：{last_q}\n"
            f"候选人答：{last_a}\n\n"
            "请输出（每条不超过15字，无则为 null）：\n"
            '{"strength": "本轮亮点或 null", "weakness": "本轮不足或 null", "note": "一句话关键观察"}'
        )

        try:
            raw = self.llm_client.generate([
                {"role": "system", "content": "你是简洁的面试评估观察员，只输出 JSON，不输出其他内容。"},
                {"role": "user", "content": prompt},
            ])
            match = re.search(r"\{[^{}]+\}", raw)
            if not match:
                print(f"[EvalObserver] turn {turn} 未解析到 JSON，raw={raw[:100]}")
                return
            obs = json.loads(match.group())
        except Exception as e:
            print(f"[EvalObserver] turn {turn} LLM 分析失败: {e}")
            return

        with self._lock:
            if self._shutdown or turn <= self.draft["last_turn"]:
                return
            if obs.get("strength"):
                self.draft["strengths"].append({"turn": turn, "text": obs["strength"]})
            if obs.get("weakness"):
                self.draft["weaknesses"].append({"turn": turn, "text": obs["weakness"]})
            if obs.get("note"):
                self.draft["turn_notes"].append({"turn": turn, "note": obs["note"]})
            self.draft["last_turn"] = turn
            snapshot = {
                "strengths": list(self.draft["strengths"]),
                "weaknesses": list(self.draft["weaknesses"]),
                "turn_notes": list(self.draft["turn_notes"]),
                "last_turn": self.draft["last_turn"],
            }
            push_callback = self._push_callback

        print(
            f"[EvalObserver] turn {turn} 草稿更新："
            f"strength={obs.get('strength')}, weakness={obs.get('weakness')}"
        )

        self._push_eval_update(turn, {
            "strength": obs.get("strength"),
            "weakness": obs.get("weakness"),
            "note": obs.get("note"),
        }, push_callback=push_callback)

        if self.data_client:
            try:
                ok = self.data_client.save_eval_draft(self.session_id, snapshot)
                if not ok:
                    print(f"[EvalObserver] turn {turn} 存储同步返回失败")
            except Exception as e:
                print(f"[EvalObserver] turn {turn} 存储同步异常: {e}")

    def get_draft(self) -> Dict:
        with self._lock:
            return {
                "strengths": list(self.draft["strengths"]),
                "weaknesses": list(self.draft["weaknesses"]),
                "turn_notes": list(self.draft["turn_notes"]),
                "last_turn": self.draft["last_turn"],
            }

    def shutdown(self, wait: bool = False, timeout: Optional[float] = None) -> Dict:
        """
        Stop accepting new work and close the observer.

        When wait=True, already-submitted tasks are given a bounded chance to
        finish before the observer is frozen. After shutdown completes, no late
        task may mutate the draft anymore.
        """
        with self._lock:
            if self._shutdown:
                return {
                    "strengths": list(self.draft["strengths"]),
                    "weaknesses": list(self.draft["weaknesses"]),
                    "turn_notes": list(self.draft["turn_notes"]),
                    "last_turn": self.draft["last_turn"],
                }
            self._accepting = False
            futures = list(self._futures)

        not_done = set()
        if wait and futures:
            _, not_done = wait_futures(futures, timeout=timeout)
        else:
            not_done = {future for future in futures if not future.done()}

        with self._lock:
            self._shutdown = True
            self._push_callback = None

        for future in list(not_done):
            future.cancel()

        try:
            self._executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            self._executor.shutdown(wait=False)

        print(f"[EvalObserver] session {self.session_id} 已关闭")
        return self.get_draft()

    def _push_eval_update(self, turn: int, eval_data: dict, push_callback=None) -> None:
        callback = push_callback if push_callback is not None else self._push_callback
        if callback:
            try:
                callback({
                    "type": "eval_update",
                    "turn": turn,
                    "data": eval_data,
                })
            except Exception as e:
                print(f"[EvalObserver] turn {turn} 推送失败：{e}")
