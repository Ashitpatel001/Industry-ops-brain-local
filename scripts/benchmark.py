#!/usr/bin/env python3
"""
scripts/benchmark.py
====================
Runs 10 industrial RAG test queries against Qwen OpenVINO INT4 backend,
measures latency, throughput (tokens/sec), and RAM footprint.

Usage:
    python scripts/benchmark.py
"""

import time
import logging
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Benchmark")

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 10 Industrial Test Queries
TEST_QUERIES = [
    "What maintenance history exists for Pump P-204 and what is the recurring failure?",
    "Check SOP-CSE-Unit5 against OISD-GDN-192 for confined space entry compliance gaps.",
    "What failure modes cause mechanical seal leaks in heat exchangers like HX-301?",
    "Calculate the risk score for asset V-112 based on recent work orders.",
    "What emergency procedures apply when OISD-116 atmospheric O2 test fails?",
    "Give me a 5-Why root cause analysis for recurring bearing failures on pump P-101.",
    "List all overdue preventive maintenance tasks and high criticality assets.",
    "What safety regulations apply under the Factory Act 1948 Section 36 for hazardous fumes?",
    "Identify systemic incident patterns across pump seal breakdowns in Unit 5.",
    "Summarize inspection report findings and relief valve testing for vessel V-205.",
]


def get_ram_usage_mb() -> int:
    """Get current process RAM usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return round(process.memory_info().rss / (1024 * 1024))
    except ImportError:
        return 0


def run_benchmark_suite():
    logger.info("==========================================================================")
    logger.info("⚡ OPS BRAIN LOCAL — INFERENCE SPEED & MEMORY BENCHMARK")
    logger.info("==========================================================================")

    # Attempt to load LocalLLM from core
    try:
        from core.model import LocalLLM
    except ImportError as e:
        logger.error(f"Could not import core.model.LocalLLM: {e}")
        logger.info("Ensure core/model.py is implemented before running benchmarks.")
        return

    from core.config import get_config
    cfg = get_config()
    model_dir = Path(cfg.model_path)

    if not model_dir.exists():
        logger.warning("No AI models found in models/ directory!")
        logger.info("Please wait for download_model.py to finish exporting Qwen OpenVINO INT4.")
        logger.info("Running in Mock Benchmark Mode for demonstration...")
        print_mock_benchmark_table()
        return

    logger.info("Loading LocalLLM engine...")
    start_load = time.time()
    try:
        llm = LocalLLM()
        load_time = round(time.time() - start_load, 2)
        logger.info(f"Model loaded in {load_time}s. Backend: {llm.backend_label}")
    except Exception as e:
        logger.error(f"Error loading LLM: {e}")
        return

    results = []
    total_tokens = 0
    total_time = 0.0

    logger.info(f"Running {len(TEST_QUERIES)} industrial test queries...")
    print("\n| # | Query Summary | Latency (s) | Tok/sec | RAM (MB) |")
    print("|---|---|---|---|---|")

    for i, q in enumerate(TEST_QUERIES, 1):
        prompt = f"<|user|>\nAnswer this industrial safety query: {q}\n<|end|>\n<|assistant|>\n"
        
        start_time = time.time()
        output = llm.generate(prompt, max_new_tokens=128, temperature=0.1)
        elapsed = time.time() - start_time
        
        # Estimate token count (approx 4 chars per token if tokenizer length unavailable)
        gen_tokens = len(output.split()) * 1.3  
        tok_sec = round(gen_tokens / max(elapsed, 0.01), 1)
        ram_mb = get_ram_usage_mb()

        results.append({
            "query": q[:40] + "...",
            "latency": round(elapsed, 2),
            "tok_sec": tok_sec,
            "ram": ram_mb
        })
        total_tokens += gen_tokens
        total_time += elapsed

        print(f"| {i} | {q[:38]}... | {round(elapsed, 2)}s | {tok_sec} | {ram_mb} MB |")

    avg_tok_sec = round(total_tokens / max(total_time, 0.01), 1)
    avg_latency = round(total_time / len(TEST_QUERIES), 2)
    final_ram = get_ram_usage_mb()

   
    print(f"BENCHMARK SUMMARY ({llm.backend_label})")
    print("==========================================================================")
    print(f"• Total Queries Tested : {len(TEST_QUERIES)}")
    print(f"• Average Latency      : {avg_latency}s per query")
    print(f"• Average Throughput   : {avg_tok_sec} tokens/sec")
    print(f"• Total Memory (RAM)   : {final_ram} MB (~{round(final_ram/1024, 1)} GB)")


def print_mock_benchmark_table():
    """Prints target architectural benchmark scores when running offline/dry-run."""
    print("\n### OpenVINO INT4 (Qwen2.5-3B) Benchmark Table")
    print("| Metric | OpenVINO INT4 (Arc GPU) | OpenVINO INT4 (Intel CPU) |")
    print("|---|---|---|")
    print("| **Model Weight Size** | **2.2 GB** | **2.2 GB** |")
    print("| **Total RAM Footprint** | **~3.1 GB** | **~3.0 GB** |")
    print("| **Time to First Token (TTFT)**| **~120 ms** | ~350 ms |")
    print("| **Throughput (Tokens/sec)** | **~35 tok/s** | **~16 tok/s** |")
    print("| **End-to-End Query Latency**| **~0.6 s** | **~1.8 s** |")
    print("| **Offline Capable?** | ✅ YES (0 bytes to cloud) | ✅ YES (0 bytes to cloud) |")
    print("\n*Note: This table reflects the target architectural benchmarks from OSDHack 2026 winning spec.*")


if __name__ == "__main__":
    run_benchmark_suite()
