# GY-63 UDP Telemetry Logger

## 1. 프로젝트 개요

- **입력**: UDP 텔레메트리 패킷 (예: `ms=...,t_x100=...,p_pa=...`)
- **처리**: 패킷 파싱 및 단위 변환(온도/압력/시간)
- **출력**: CSV 파일 저장 및 실시간 그래프 표시

## 2. 디렉터리 구조

```text
├─logs/
│   └─ udp_log_*.csv                 # 실행 시 생성되는 CSV 로그 파일
│
└─src/
    └─core/
        ├─ __init__.py               # 패키지 초기화
        ├─ __main__.py               # 엔트리포인트 (python -m core)
        ├─ app.py                    # 애플리케이션 구동/자원 관리
        ├─ config.py                 # 설정(호스트/포트/버퍼/플롯 주기/백엔드 등)
        ├─ udp_receiver.py           # UDP 수신 스레드 + 패킷 파싱 + 샘플 생성
        ├─ logger.py                 # CSV 로깅(파일 생성/헤더/flush/close)
        └─ plotter.py                # matplotlib 기반 실시간 플롯
```

## 4. 실행 방법

본 프로젝트는 `src/` 하위에 패키지가 위치하므로, 실행 시 `PYTHONPATH=src` 설정이 필요합니다.

- **방화벽(Windows Defender Firewall 등)이 활성화되어 있으면 UDP 수신이 차단될 수 있으므로, 실행 전 방화벽을 비활성화하거나 해당 포트(기본 `5005/UDP`)에 대한 인바운드 허용 규칙을 설정해야 합니다.**
- **수신 PC의 네트워크 인터페이스 IP가 `192.168.144.201`로 설정되어 있어야 합니다.**  
  (송신 측 MCU가 해당 IP로 UDP 패킷을 전송하는 구성을 전제)

### Windows (PowerShell)

```powershell
$env:PYTHONPATH="src"
python -m core
```

## 5. 의존성
- Python 3.x
- matplotlib
```powershell
pip install matplotlib
```
> matplotlib 백엔드는 기본값으로 TkAgg를 사용하며, 환경에 따라 QtAgg로 변경이 필요할 수 있습니다. (src/core/config.py 참고)


## 6. 데이터 포맷

수신 패킷은 기본적으로 다음 키를 포함하는 k=v 콤마 구분 문자열을 가정합니다.

```예시 패킷:
ms=59957,t_x100=2844,p_pa=101847
```

## 7. 산출물
- logs/udp_log_YYYYmmdd_HHMMSS.csv 형태로 CSV 로그가 생성됩니다.