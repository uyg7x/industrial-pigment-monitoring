from tkinter import messagebox, ttk
from app.ui.common import section
from app.services.export_service import export_excel


def build(parent, process_df, inventory_df, delivery_df):
    frame = section(parent, 'Reports and Export', 'Generate ready-to-share Excel reports for operations')

    def do_export():
        path = export_excel(process_df, inventory_df, delivery_df)
        messagebox.showinfo('Export complete', f'Report saved to:\n{path}')

    ttk.Button(frame, text='Export Excel Report', command=do_export).pack(anchor='w')
    ttk.Label(frame, text='Exports are saved inside the exports folder.', style='Card.TLabel').pack(anchor='w', pady=(8, 0))
    frame.pack(fill='x', padx=10, pady=10)
