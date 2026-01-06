from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional


@dataclass(frozen=True)
class TelemetrySample:
    pc_time_iso: str
    src_ip: str
    src_port: int
    ms: int
    t_c: float
    p_pa: int
    p_hpa: float
    x_s: float  # ms/1000


def parse_packet(text: str) -> dict:
    out = {}
    for p in text.strip().split(","):
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        k, v = k.strip(), v.strip()
        try:
            out[k] = int(v)
        except ValueError:
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    return out


def parse_gy63(text: str, addr: tuple[str, int]) -> Optional[TelemetrySample]:
    d = parse_packet(text)

    if "ms" not in d or "t_x100" not in d or "p_pa" not in d:
        return None

    ms = int(float(d["ms"]))
    t_c = float(d["t_x100"]) / 100.0
    p_pa = int(float(d["p_pa"]))
    p_hpa = p_pa / 100.0
    x_s = ms / 1000.0

    return TelemetrySample(
        pc_time_iso=datetime.now().isoformat(timespec="milliseconds"),
        src_ip=addr[0],
        src_port=addr[1],
        ms=ms,
        t_c=t_c,
        p_pa=p_pa,
        p_hpa=p_hpa,
        x_s=x_s,
    )


class UDPReceiver:
    """
    UDP 수신을 별도 스레드에서 수행하고, 패킷을 TelemetrySample로 파싱해 콜백으로 전달.
    """
    def __init__(
        self,
        host: str,
        port: int,
        on_sample: Callable[[TelemetrySample], None],
        stop_event: threading.Event,
        *,
        recv_buf: int = 2048,
        timeout_s: float = 0.5,
    ):
        self._host = host
        self._port = port
        self._on_sample = on_sample
        self._stop = stop_event
        self._recv_buf = recv_buf

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((host, port))
        self._sock.settimeout(timeout_s)

        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def close(self) -> None:
        # stop_event는 app에서 관리. 여기서는 소켓/스레드 정리만.
        try:
            self._sock.close()
        except Exception:
            pass

        if self._thread:
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(self._recv_buf)
            except socket.timeout:
                continue
            except OSError:
                # 소켓 close로 인해 발생 가능
                break

            text = data.decode(errors="replace").strip()
            s = parse_gy63(text, addr)
            if s is None:
                continue

            self._on_sample(s)
