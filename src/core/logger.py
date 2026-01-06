from __future__ import annotations

import csv
import os
from datetime import datetime

from .udp_receiver import TelemetrySample


class CSVLogger:
    def __init__(self, logs_dir: str):
        os.makedirs(logs_dir, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(logs_dir, f"udp_log_{ts}.csv")

        self._f = open(self.path, "a", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(
            self._f,
            fieldnames=["pc_time_iso", "src_ip", "src_port", "ms", "t_c", "p_pa", "p_hpa"],
        )
        self._writer.writeheader()
        self._f.flush()

    def write(self, s: TelemetrySample) -> None:
        self._writer.writerow({
            "pc_time_iso": s.pc_time_iso,
            "src_ip": s.src_ip,
            "src_port": s.src_port,
            "ms": s.ms,
            "t_c": s.t_c,
            "p_pa": s.p_pa,
            "p_hpa": s.p_hpa,
        })

    def flush(self) -> None:
        self._f.flush()

    def close(self) -> None:
        try:
            self._f.flush()
        finally:
            self._f.close()
