from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from tabulate import tabulate

from agent_advanced import AdvancedAgent
from agent_baseline import BaselineAgent
from config import load_config


@dataclass
class BenchmarkRow:
    agent_name: str
    agent_tokens_only: int
    prompt_tokens_processed: int
    recall_score: float
    response_quality: float
    memory_growth_bytes: int
    compactions: int


def load_conversations(path: Path) -> list[dict[str, Any]]:
    """Student TODO: read JSON conversations from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def recall_points(answer: str, expected: list[str]) -> float:
    """Student TODO: return 0 / 0.5 / 1 depending on how many expected facts appear."""
    ans = answer.lower()
    matches = 0
    for e in expected:
        if e.lower() in ans:
            matches += 1
    if matches == 0:
        return 0.0
    if matches == len(expected):
        return 1.0
    return 0.5


def heuristic_quality(answer: str, expected: list[str]) -> float:
    """Student TODO: add a lightweight quality score for offline mode."""
    return recall_points(answer, expected)


def run_agent_benchmark(agent_name: str, agent, conversations: list[dict[str, Any]], config) -> BenchmarkRow:
    """Student TODO: evaluate one agent over many conversations."""
    total_tokens = 0
    total_prompt_tokens = 0
    total_recall = 0.0
    total_quality = 0.0
    total_compactions = 0
    total_memory_growth = 0
    num_questions = 0
    
    for conv in conversations:
        user_id = conv["user_id"]
        thread_id = conv["id"]
        
        # Feed all turns to the agent
        for turn in conv.get("turns", []):
            agent.reply(user_id, thread_id, turn)
            
        total_tokens += agent.token_usage(thread_id)
        total_prompt_tokens += agent.prompt_token_usage(thread_id)
        total_compactions += agent.compaction_count(thread_id)
        
        # Memory file growth
        if hasattr(agent, "memory_file_size"):
            total_memory_growth += agent.memory_file_size(user_id)
            
        # Recall questions in fresh thread
        for q in conv.get("recall_questions", []):
            fresh_thread = thread_id + "_recall_0"
            resp = agent.reply(user_id, fresh_thread, q["question"])
            ans = resp["response"]
            
            expected = q["expected_contains"]
            recall = recall_points(ans, expected)
            total_recall += recall
            total_quality += heuristic_quality(ans, expected)
            num_questions += 1
            
    avg_recall = total_recall / max(1, num_questions) if num_questions > 0 else 0.0
    avg_quality = total_quality / max(1, num_questions) if num_questions > 0 else 0.0
    
    return BenchmarkRow(
        agent_name=agent_name,
        agent_tokens_only=total_tokens,
        prompt_tokens_processed=total_prompt_tokens,
        recall_score=avg_recall,
        response_quality=avg_quality,
        memory_growth_bytes=total_memory_growth,
        compactions=total_compactions
    )


def format_rows(rows: list[BenchmarkRow]) -> str:
    """Student TODO: print a markdown table or tabulated output."""
    headers = [
        "Agent Name", "Agent tokens only", "Prompt tokens processed", 
        "Cross-session recall", "Response quality", "Memory growth (bytes)", "Compactions"
    ]
    data = []
    for r in rows:
        data.append([
            r.agent_name,
            r.agent_tokens_only,
            r.prompt_tokens_processed,
            f"{r.recall_score:.2f}",
            f"{r.response_quality:.2f}",
            r.memory_growth_bytes,
            r.compactions
        ])
    return tabulate(data, headers=headers, tablefmt="github")


def main() -> None:
    """Student TODO: run both benchmark suites."""
    
    config = load_config(Path(__file__).resolve().parent.parent)
    data_dir = config.data_dir
    
    # Standard benchmark
    try:
        std_convs = load_conversations(data_dir / "conversations.json")
        baseline = BaselineAgent(config=config, force_offline=True)
        advanced = AdvancedAgent(config=config, force_offline=True)
        
        row1 = run_agent_benchmark("Baseline", baseline, std_convs, config)
        row2 = run_agent_benchmark("Advanced", advanced, std_convs, config)
        
        print("\n### Standard Benchmark")
        print(format_rows([row1, row2]))
    except Exception as e:
        print(f"Error running standard benchmark: {e}")

    # Long-context stress benchmark
    try:
        stress_convs = load_conversations(data_dir / "advanced_long_context.json")
        # reset agents
        baseline_stress = BaselineAgent(config=config, force_offline=True)
        advanced_stress = AdvancedAgent(config=config, force_offline=True)
        
        row3 = run_agent_benchmark("Baseline (Stress)", baseline_stress, stress_convs, config)
        row4 = run_agent_benchmark("Advanced (Stress)", advanced_stress, stress_convs, config)
        
        print("\n### Long-Context Stress Benchmark")
        print(format_rows([row3, row4]))
    except Exception as e:
        print(f"Error running stress benchmark: {e}")

if __name__ == "__main__":
    main()
