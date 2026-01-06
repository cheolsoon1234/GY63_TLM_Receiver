from __future__ import annotations

import threading
from collections import deque

from .config import AppConfig


def run_live_plot(
    cfg: AppConfig,
    stop_event: threading.Event,
    lock: threading.Lock,
    x_s: deque,
    t_c: deque,
    p_hpa: deque,
) -> None:

    import matplotlib
    matplotlib.use(cfg.matplotlib_backend)

    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fig, (ax_t, ax_p) = plt.subplots(2, 1, sharex=True)

    ax_t.set_title("Temperature")
    ax_t.set_ylabel("°C")
    (line_t,) = ax_t.plot([], [], linewidth=1)

    ax_p.set_title("Pressure")
    ax_p.set_ylabel("hPa")
    ax_p.set_xlabel("Time since boot (s)")
    (line_p,) = ax_p.plot([], [], linewidth=1)

    def animate(_):
        with lock:
            if len(x_s) < 2:
                return line_t, line_p
            xs = list(x_s)
            tc = list(t_c)
            ph = list(p_hpa)

        line_t.set_data(xs, tc)
        line_p.set_data(xs, ph)

        ax_t.relim(); ax_t.autoscale_view()
        ax_p.relim(); ax_p.autoscale_view()

        return line_t, line_p

    def _on_close(_evt):
        stop_event.set()

    fig.canvas.mpl_connect("close_event", _on_close)

    # 반드시 참조 유지(가비지컬렉션 방지)
    ani = FuncAnimation(
        fig,
        animate,
        interval=cfg.anim_interval_ms,
        blit=False,
        cache_frame_data=False,
    )

    plt.tight_layout()
    plt.show()
    _ = ani  # lint 방지용(참조 유지)
