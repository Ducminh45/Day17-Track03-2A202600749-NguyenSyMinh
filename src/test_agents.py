from __future__ import annotations

import pytest
from pathlib import Path

from agent_advanced import AdvancedAgent
from agent_baseline import BaselineAgent
from config import LabConfig, load_config
from model_provider import ProviderConfig
from memory_store import UserProfileStore


def make_config(tmp_path: Path):
    """Student TODO: build an isolated config for tests."""
    model_config = ProviderConfig(provider="custom", model_name="mock", temperature=0.0)
    return LabConfig(
        base_dir=tmp_path,
        data_dir=tmp_path / "data",
        state_dir=tmp_path / "state",
        compact_threshold_tokens=50,
        compact_keep_messages=1,
        model=model_config,
        judge_model=model_config
    )


def test_user_markdown_read_write_edit(tmp_path: Path) -> None:
    """Student TODO: verify `User.md` can be created, updated, and edited."""
    store = UserProfileStore(tmp_path)
    user_id = "test_user"
    
    # Read empty
    assert store.read_text(user_id) == ""
    
    # Write
    store.write_text(user_id, "name: Test\nprofession: Dev\n")
    assert "name: Test" in store.read_text(user_id)
    assert store.file_size(user_id) > 0
    
    # Edit
    changed = store.edit_text(user_id, "profession: Dev", "profession: Engineer")
    assert changed is True
    assert "profession: Engineer" in store.read_text(user_id)


def test_compact_trigger(tmp_path: Path) -> None:
    """Student TODO: verify long threads trigger compaction."""
    config = make_config(tmp_path)
    agent = AdvancedAgent(config=config, force_offline=True)
    
    thread_id = "thread_compact"
    for i in range(10):
        agent.reply("user_1", thread_id, f"Đây là tin nhắn thứ {i} với độ dài nhất định để kiểm tra tính năng nén bộ nhớ hoạt động chính xác.")
        
    assert agent.compaction_count(thread_id) > 0


def test_cross_session_recall(tmp_path: Path) -> None:
    """Student TODO: verify advanced remembers across sessions and baseline does not."""
    config = make_config(tmp_path)
    
    baseline = BaselineAgent(config=config, force_offline=True)
    baseline.reply("user_2", "thread_b_1", "Tên tôi là DũngCT.")
    res_b = baseline.reply("user_2", "thread_b_2", "Mình tên gì?")
    assert "DũngCT" not in res_b["response"]
    
    advanced = AdvancedAgent(config=config, force_offline=True)
    advanced.reply("user_2", "thread_a_1", "Tên tôi là DũngCT.")
    res_a = advanced.reply("user_2", "thread_a_2", "Mình tên gì?")
    assert "DũngCT" in res_a["response"]


def test_compact_reduces_prompt_load_on_long_thread(tmp_path: Path) -> None:
    """Student TODO: compare prompt load of baseline vs advanced on a long thread."""
    config = make_config(tmp_path)
    
    baseline = BaselineAgent(config=config, force_offline=True)
    advanced = AdvancedAgent(config=config, force_offline=True)
    
    thread_id = "thread_long"
    for i in range(20):
        msg = f"Đây là một tin nhắn rất dài lặp lại nhiều lần. Số {i}. " * 5
        baseline.reply("user_3", thread_id, msg)
        advanced.reply("user_3", thread_id, msg)
        
    b_tokens = baseline.prompt_token_usage(thread_id)
    a_tokens = advanced.prompt_token_usage(thread_id)
    
    # Advanced should be much lower because it compresses memory
    assert a_tokens < b_tokens
