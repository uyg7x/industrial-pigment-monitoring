from matplotlib.figure import Figure


def make_line(df, x, y, title):
    fig = Figure(figsize=(6.2, 3.2), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(df[x], df[y], marker='o')
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=45)
    fig.tight_layout()
    return fig
