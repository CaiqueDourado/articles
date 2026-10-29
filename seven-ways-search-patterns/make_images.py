"""Cover and the patterns-per-algorithm chart of the article (EN and PT). Run: python make_images.py"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, LINE, BG, CARD, BLUE, GREEN, ORANGE = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff", "#2a78d6", "#1baf7a", "#b4531f"
MONO = "DejaVu Sans Mono"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

COVER = {"": ("Seven ways to turn millions of\nGoogle searches into page templates",
              "How I grouped 38 million searches to choose which sites to build (2017–2019)", "part 1 of 3"),
         ".pt-BR": ("Sete jeitos de transformar milhões de\nbuscas do Google em modelos de página",
                    "Como agrupei 38 milhões de buscas para escolher quais sites construir (2017–2019)", "parte 1 de 3")}
ROWS = [("como fazer panqueca", "como fazer pudim", "como fazer bolo de cenoura", "com faz [comida]"),
        ("apartamento para alugar em curitiba", "casa para alugar em goiânia", "kitnet para alugar em natal", "[imovel] par alug [cidade]")]


def cover():
    for suf, (title, sub, part) in COVER.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, title, fontsize=30, weight="bold", color=INK, va="top", linespacing=1.15)
        ax.text(6, 43.5, sub, fontsize=14, color=MUTED, va="center")
        for k, (a, b, c, p) in enumerate(ROWS):
            x = 6 + k * 66
            ax.add_patch(FancyBboxPatch((x, 7), 62, 29, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=LINE, lw=1.2))
            for i, s in enumerate((a, b, c)):
                ax.text(x + 3, 31 - i * 5, s, fontsize=12.5, color=INK, family=MONO, va="center")
            ax.text(x + 3, 13, "→ " + p, fontsize=15, color=GREEN, family=MONO, weight="bold", va="center")
        ax.text(6, 2.8, "github.com/CaiqueDourado/search-pattern-miner", fontsize=11, color=MUTED)
        ax.text(134, 2.8, part, fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


ALG = [  # published table padroes_algoritmos (google-keywords-dataset)
    ("prefix", "prefixo", 779223, "previsa temp", "previsão do tempo"),
    ("entity prefix", "prefixo com entidade", 466369, "receit [comida]", "receita de bolo"),
    ("entity skip-gram", "skip-gram com entidade", 254802, "[imovel] par [local]", "apartamentos para alugar em curitiba"),
    ("contiguous", "sequência", 202320, "nacional ensin medi", "exame nacional do ensino médio"),
    ("entity contiguous", "sequência com entidade", 28522, "[-bebes] [marca]", "fraldas huggies"),
]
CH = {"": ("Patterns found by each algorithm", "1.73 million published patterns; the example is a real pattern and its leading search",
           "Source: google-keywords-dataset"),
      ".pt-BR": ("Padrões encontrados por algoritmo", "1,73 milhão de padrões publicados; o exemplo é um padrão real e a busca que o lidera",
                 "Fonte: google-keywords-dataset")}


def chart():
    for suf, (t, s, src) in CH.items():
        pt = bool(suf)
        fig, ax = plt.subplots(figsize=(11, 5.6), dpi=110)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        rows = ALG[::-1]
        ax.barh([r[1] if pt else r[0] for r in rows], [r[2] for r in rows], color=BLUE, height=0.62)
        mx = ALG[0][2]
        for i, r in enumerate(rows):
            n = f"{r[2]:,}".replace(",", ".") if pt else f"{r[2]:,}"
            ax.text(r[2] + mx * 0.01, i + 0.13, n, fontsize=11, weight="bold", color=INK, va="center")
            ax.text(r[2] + mx * 0.01, i - 0.2, f"{r[3]}  ←  {r[4]}", fontsize=9.5, color=MUTED, va="center", family=MONO)
        for sp in ("top", "right", "left", "bottom"):
            ax.spines[sp].set_visible(False)
        ax.xaxis.set_visible(False)
        ax.tick_params(colors=INK, labelsize=10.5, length=0)
        ax.set_xlim(0, mx * 1.75)
        fig.text(0.02, 0.94, t, fontsize=17, weight="bold", color=INK)
        fig.text(0.02, 0.895, s, fontsize=10.5, color=MUTED)
        fig.text(0.02, 0.02, src, fontsize=8.5, color=MUTED)
        fig.subplots_adjust(left=0.2, right=0.98, top=0.84, bottom=0.07)
        fig.savefig(OUT / f"algorithms{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    cover()
    chart()
