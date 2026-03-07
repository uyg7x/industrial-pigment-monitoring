from tkinter import ttk


def data_table(parent, df, height=10):
    cols = list(df.columns)
    frame = ttk.Frame(parent, style='Card.TFrame')
    tree = ttk.Treeview(frame, columns=cols, show='headings', height=height)
    ys = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    xs = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor='center')
    for row in df.head(25).itertuples(index=False):
        tree.insert('', 'end', values=list(row))
    tree.grid(row=0, column=0, sticky='nsew')
    ys.grid(row=0, column=1, sticky='ns')
    xs.grid(row=1, column=0, sticky='ew')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    return frame
