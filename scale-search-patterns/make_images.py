"""Cover and the scale chart of part 2 (EN and PT). Run: python make_images.py"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, LINE, BG, CARD, BLUE, ORANGE, GREEN = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff", "#2a78d6", "#eb6834", "#1baf7a"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

COVER = {"": ("Almost 400 million search patterns,\nfive databases, and what actually worked",
              "Grouping 38 million Google searches in 2018, and doing it again in 2026", "part 2 of 3",
              [("54.95 M", "searches with volume"), ("141 M", "search → pattern pairs"), ("396 M", "skip-gram documents"),
               ("57.7 B", "string comparisons")]),
         ".pt-BR": ("Quase 400 milhões de padrões de busca,\ncinco bancos de dados e o que de fato funcionou",
                    "Agrupando 38 milhões de buscas do Google em 2018, e de novo em 2026", "parte 2 de 3",
                    [("54,95 mi", "buscas com volume"), ("141 mi", "pares busca → padrão"), ("396 mi", "documentos de skip-gram"),
                     ("57,7 bi", "comparações de texto")])}


def cover():
    for suf, (title, sub, part, nums) in COVER.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, title, fontsize=29, weight="bold", color=INK, va="top", linespacing=1.15)
        ax.text(6, 43.5, sub, fontsize=14, color=MUTED, va="center")
        for i, (n, label) in enumerate(nums):
            x = 6 + i * 32.5
            ax.add_patch(FancyBboxPatch((x, 9), 29.5, 26, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=LINE, lw=1.2))
            ax.text(x + 2.5, 25, n, fontsize=27, weight="bold", color=(BLUE, BLUE, ORANGE, ORANGE)[i], va="center")
            ax.text(x + 2.5, 15, label, fontsize=12.5, color=MUTED, va="center")
        ax.text(6, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED)
        ax.text(134, 2.8, part, fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


SCALE = [  # from the 2018 code and the published dataset
    ("searches in the published dataset", "buscas no dataset publicado", 37_961_526, BLUE),
    ("search rows collected (2 batches)", "linhas de busca coletadas (2 lotes)", 54_950_000, BLUE),
    ("search → pattern pairs", "pares busca → padrão", 141_000_000, BLUE),
    ("search ↔ group links (checkpoint)", "ligações busca ↔ grupo (checkpoint)", 200_477_319, BLUE),
    ("skip-gram documents (checkpoint)", "documentos de skip-gram (checkpoint)", 396_320_000, ORANGE),
    ("string pairs compared (checkpoint)", "pares de texto comparados (checkpoint)", 57_708_899_736, ORANGE),
]
CH = {"": ("The sizes, on a log scale", "From the dataset I published to the comparisons I tried; checkpoints are lower bounds", "Source: the 2018 code (counters and checkpoints) and google-keywords-dataset"),
      ".pt-BR": ("Os tamanhos, em escala log", "Do dataset que publiquei às comparações que tentei; checkpoints são limites mínimos", "Fonte: o código de 2018 (contadores e checkpoints) e o google-keywords-dataset")}


def human(n, pt):
    for div, en, ptu in ((1e9, "B", "bi"), (1e6, "M", "mi")):
        if n >= div:
            s = f"{n / div:.1f}"
            return (s.replace(".", ",") + " " + ptu) if pt else (s + " " + en)
    return str(n)


def chart():
    for suf, (t, s, src) in CH.items():
        pt = bool(suf)
        fig, ax = plt.subplots(figsize=(11, 5.2), dpi=110)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        rows = SCALE[::-1]
        ax.barh([r[1] if pt else r[0] for r in rows], [r[2] for r in rows], color=[r[3] for r in rows], height=0.6)
        ax.set_xscale("log")
        for i, r in enumerate(rows):
            ax.text(r[2] * 1.15, i, human(r[2], pt), fontsize=11, weight="bold", color=INK, va="center")
        for sp in ("top", "right", "left", "bottom"):
            ax.spines[sp].set_visible(False)
        ax.xaxis.set_visible(False)
        ax.tick_params(colors=INK, labelsize=10.5, length=0)
        ax.set_xlim(1e7, 1e12)
        fig.text(0.02, 0.94, t, fontsize=17, weight="bold", color=INK)
        fig.text(0.02, 0.895, s, fontsize=10.5, color=MUTED)
        fig.text(0.02, 0.02, src, fontsize=8.5, color=MUTED)
        fig.subplots_adjust(left=0.31, right=0.98, top=0.84, bottom=0.07)
        fig.savefig(OUT / f"scale{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    cover()
    chart()
