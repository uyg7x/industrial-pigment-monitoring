from datetime import datetime
from app.utils.helpers import EXPORT_DIR


def export_excel(process_df, inventory_df, delivery_df):
    path = EXPORT_DIR / f"pigment_report_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    with __import__('pandas').ExcelWriter(path, engine='openpyxl') as writer:
        process_df.to_excel(writer, sheet_name='Process', index=False)
        inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
        delivery_df.to_excel(writer, sheet_name='Deliveries', index=False)
    return path
