from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 5005

    max_points: int = 2000
    anim_interval_ms: int = 100

    logs_dir: str = "logs"
    flush_every: int = 20

    matplotlib_backend: str = "TkAgg"  # 갱신 안 되면 "QtAgg" 시도
