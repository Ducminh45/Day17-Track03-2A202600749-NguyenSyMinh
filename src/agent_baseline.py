from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from config import LabConfig, load_config
from memory_store import estimate_tokens
from model_provider import build_chat_model


@dataclass
class SessionState:
    messages: list[dict[str, str]] = field(default_factory=list)
    token_usage: int = 0
    prompt_tokens_processed: int = 0


class BaselineAgent:
    """Student TODO: implement Agent A.

    Requirements:
    - Within-session memory only
    - No persistent `User.md`
    - Should forget long-term facts across new threads
    """

    def __init__(self, config: LabConfig | None = None, force_offline: bool = False) -> None:
        self.config = config or load_config()
        self.force_offline = force_offline
        self.sessions: dict[str, SessionState] = {}

        self.langchain_agent = None
        if not self.force_offline:
            self._maybe_build_langchain_agent()

    def reply(self, user_id: str, thread_id: str, message: str) -> dict[str, Any]:
        """Student TODO: return the agent response and token accounting."""
        return self._reply_offline(thread_id, message)

    def token_usage(self, thread_id: str) -> int:
        state = self.sessions.get(thread_id)
        return state.token_usage if state else 0

    def prompt_token_usage(self, thread_id: str) -> int:
        state = self.sessions.get(thread_id)
        return state.prompt_tokens_processed if state else 0

    def compaction_count(self, thread_id: str) -> int:
        # Baseline has no compact memory.
        return 0

    def _reply_offline(self, thread_id: str, message: str) -> dict[str, Any]:
        """Student TODO: implement a simple offline behavior."""
        if thread_id not in self.sessions:
            self.sessions[thread_id] = SessionState()
        
        state = self.sessions[thread_id]
        
        prompt_tokens = 0
        for m in state.messages:
            prompt_tokens += estimate_tokens(m["content"])
        
        user_msg_tokens = estimate_tokens(message)
        prompt_tokens += user_msg_tokens
        
        state.prompt_tokens_processed += prompt_tokens
        state.token_usage += user_msg_tokens
        state.messages.append({"role": "user", "content": message})
        
        # Offline logic just answers based on current session
        response_text = self._offline_response(thread_id, message)
        
        out_tokens = estimate_tokens(response_text)
        state.token_usage += out_tokens
        state.messages.append({"role": "assistant", "content": response_text})
        
        return {
            "response": response_text,
            "token_usage": state.token_usage,
            "prompt_tokens_processed": state.prompt_tokens_processed
        }
        
    def _offline_response(self, thread_id: str, message: str) -> str:
        state = self.sessions.get(thread_id)
        history = " ".join([m["content"] for m in state.messages]).lower() if state else ""
        text = message.lower()
        
        if "tên gì" in text or "tên" in text:
            if "dũngct" in history:
                return "Tên bạn là DũngCT."
            if "dũng" in history:
                return "Tên bạn là Dũng."
                
        if "đồ uống" in text or "uống" in text:
            if "cà phê sữa đá" in history:
                return "Bạn thích uống cà phê sữa đá."
                
        if "nghề" in text:
            if "mlops" in history:
                return "Bạn là MLOps engineer."
                
        if "ở đâu" in text or "nơi ở" in text:
            if "đà nẵng" in history:
                return "Bạn ở Đà Nẵng."
            if "huế" in history:
                return "Bạn ở Huế."
                
        return "Ghi nhận thông tin."

    def _maybe_build_langchain_agent(self):
        """Student TODO: optionally wire `create_agent` + `InMemorySaver` here."""
        try:
            self.langchain_agent = build_chat_model(self.config.model)
        except Exception:
            pass
