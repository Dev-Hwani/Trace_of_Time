from __future__ import annotations

import itertools
import json
import statistics
import threading
import time
from dataclasses import dataclass
from typing import Any

import requests
import uvicorn
from fastapi import FastAPI

from app.routers import memory as memory_router
from app.schemas.memory_schema import MemoryInput

# Synthetic AI latency to emulate GPT + image generation time.
GPT_DELAY_SEC = 1.0
IMAGE_DELAY_SEC = 1.0

# Benchmark settings.
WARMUP_REQUESTS = 3
MEASURE_REQUESTS = 15
ASYNC_PORT = 8121
SYNC_PORT = 8122


_id_counter = itertools.count(1)
_memory_store: dict[int, dict[str, Any]] = {}


def fake_save_memory(text, memory_date, gpt_analysis, image_url):
    memory_id = next(_id_counter)
    _memory_store[memory_id] = {
        "id": memory_id,
        "text": text,
        "date": str(memory_date),
        "gpt_analysis": gpt_analysis,
        "image_url": image_url,
    }
    return memory_id


def fake_update_memory(memory_id, text, memory_date, gpt_analysis, image_url):
    if memory_id not in _memory_store:
        return False
    _memory_store[memory_id].update(
        {
            "text": text,
            "date": str(memory_date),
            "gpt_analysis": gpt_analysis,
            "image_url": image_url,
        }
    )
    return True


def fake_analyze_memory(text: str) -> dict[str, str]:
    time.sleep(GPT_DELAY_SEC)
    return {
        "emotion": "nostalgia",
        "imagery": f"memory of {text}",
        "time_period": "past",
        "symbolism": "photo album",
    }


def fake_generate_image(prompt_or_gpt_result) -> str:
    time.sleep(IMAGE_DELAY_SEC)
    return "https://example.com/mock-image.png"


# Patch external dependencies with deterministic fakes.
memory_router.save_memory = fake_save_memory
memory_router.update_memory = fake_update_memory
memory_router.analyze_memory = fake_analyze_memory
memory_router.generate_image = fake_generate_image


async_app = FastAPI(title="async-benchmark-app")
async_app.include_router(memory_router.router, prefix="/memory")


@async_app.get("/health")
async def async_health():
    return {"ok": True}


sync_app = FastAPI(title="sync-benchmark-app")


@sync_app.get("/health")
async def sync_health():
    return {"ok": True}


@sync_app.post("/memory/create")
def create_memory_sync(memory: MemoryInput):
    memory_id = fake_save_memory(memory.text, memory.date, {"status": "processing"}, "")
    memory_router._process_memory(memory_id, memory.text, memory.date)
    return {"status": "done", "memory_id": memory_id}


@dataclass
class ServerHandle:
    server: uvicorn.Server
    thread: threading.Thread
    port: int


def start_server(app: FastAPI, port: int) -> ServerHandle:
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=port,
        log_level="error",
        access_log=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    wait_until_ready(port)
    return ServerHandle(server=server, thread=thread, port=port)


def stop_server(handle: ServerHandle):
    handle.server.should_exit = True
    handle.thread.join(timeout=5)


def wait_until_ready(port: int, timeout_sec: float = 10.0):
    deadline = time.time() + timeout_sec
    health_url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        try:
            response = requests.get(health_url, timeout=0.3)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise RuntimeError(f"Server on port {port} did not become ready.")


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    index = int(round((len(sorted_vals) - 1) * p))
    return sorted_vals[index]


def benchmark_create_endpoint(base_url: str) -> list[float]:
    times_ms: list[float] = []
    session = requests.Session()

    for i in range(WARMUP_REQUESTS + MEASURE_REQUESTS):
        payload = {"text": f"memory-{i}", "date": "2026-03-01"}
        start = time.perf_counter()
        response = session.post(f"{base_url}/memory/create", json=payload, timeout=30)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if response.status_code not in (200, 202):
            raise RuntimeError(f"Unexpected status: {response.status_code}, body={response.text}")

        if i >= WARMUP_REQUESTS:
            times_ms.append(elapsed_ms)

    return times_ms


def summarize(times_ms: list[float]) -> dict[str, float]:
    return {
        "mean_ms": round(statistics.fmean(times_ms), 2),
        "p50_ms": round(statistics.median(times_ms), 2),
        "p95_ms": round(percentile(times_ms, 0.95), 2),
        "min_ms": round(min(times_ms), 2),
        "max_ms": round(max(times_ms), 2),
    }


def main():
    async_server = start_server(async_app, ASYNC_PORT)
    sync_server = start_server(sync_app, SYNC_PORT)

    try:
        async_times = benchmark_create_endpoint(f"http://127.0.0.1:{ASYNC_PORT}")
        sync_times = benchmark_create_endpoint(f"http://127.0.0.1:{SYNC_PORT}")
    finally:
        stop_server(async_server)
        stop_server(sync_server)

    async_stats = summarize(async_times)
    sync_stats = summarize(sync_times)

    mean_improvement_pct = ((sync_stats["mean_ms"] - async_stats["mean_ms"]) / sync_stats["mean_ms"]) * 100
    speedup = sync_stats["mean_ms"] / async_stats["mean_ms"]

    result = {
        "config": {
            "gpt_delay_sec": GPT_DELAY_SEC,
            "image_delay_sec": IMAGE_DELAY_SEC,
            "warmup_requests": WARMUP_REQUESTS,
            "measure_requests": MEASURE_REQUESTS,
        },
        "before_sync_stats_ms": sync_stats,
        "after_async_stats_ms": async_stats,
        "improvement": {
            "mean_response_time_reduction_pct": round(mean_improvement_pct, 2),
            "mean_speedup_x": round(speedup, 2),
        },
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
