from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / 'data'
EXPORT_DIR = ROOT_DIR / 'exports'
EXPORT_DIR.mkdir(exist_ok=True)


def pct(value: float) -> str:
    return f'{value:.1f}%'


def num(value: float) -> str:
    return f'{value:.2f}'
