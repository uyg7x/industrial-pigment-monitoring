from pathlib import Path
import pandas as pd
from app.utils.helpers import DATA_DIR

PROCESS_FILE = DATA_DIR / 'process_data.csv'
INVENTORY_FILE = DATA_DIR / 'inventory_data.csv'
DELIVERY_FILE = DATA_DIR / 'delivery_data.csv'


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_process(path: str | None = None) -> pd.DataFrame:
    df = _read_csv(Path(path) if path else PROCESS_FILE)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df


def load_inventory() -> pd.DataFrame:
    return _read_csv(INVENTORY_FILE)


def load_deliveries() -> pd.DataFrame:
    return _read_csv(DELIVERY_FILE)
