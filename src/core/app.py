from __future__ import annotations

import os
import threading
from collections import deque

from .config import AppConfig
from .logger import CSVLogger
from .plotter import run_live_plot
from .udp_receiver import UDPReceiver, TelemetrySample


def main() -> None:
    cfg = AppConfig()

    # ---- 공유 버퍼(메모리 고정: deque maxlen) ----
    x_s = deque(maxlen=cfg.max_points)
    t_c = deque(maxlen=cfg.max_points)
    p_hpa = deque(maxlen=cfg.max_points)
    lock = threading.Lock()

    stop_event = threading.Event()

    # ---- CSV ----
    logger = CSVLogger(cfg.logs_dir)

    pkt_count = 0

    def on_sample(s: TelemetrySample) -> None:
        nonlocal pkt_count

        with lock:
            x_s.append(s.x_s)
            t_c.append(s.t_c)
            p_hpa.append(s.p_hpa)

        logger.write(s)

        pkt_count += 1
        if pkt_count % cfg.flush_every == 0:
            logger.flush()

    # ---- UDP ----
    rx = UDPReceiver(cfg.host, cfg.port, on_sample, stop_event)
    rx.start()

    print(f"Listening UDP on {cfg.host}:{cfg.port}")
    print(f"Logging to: {os.path.abspath(logger.path)}")

    try:
        run_live_plot(cfg, stop_event, lock, x_s, t_c, p_hpa)
    finally:
        stop_event.set()
        try:
            rx.close()
        except Exception:
            pass
        try:
            logger.close()
        except Exception:
            pass
