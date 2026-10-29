"""Images of the article on the 50-million-search spreadsheet (EN and PT): cover and the volume-per-search chart.
Run: python make_images.py

Numbers from google-keywords-dataset (github.com/CaiqueDourado/google-keywords-dataset):
- sample/padroes_sample.csv, the SuperNichos prefix table, Brazilian rows (num_buscas, volume_total);
- README "Cleaning": 18.3 million of the 44.6 million 2018 rows had volume 0, meaning "no metric" (41%);
- sample/padroes_sample.csv: median cpc_medio of BR patterns, 1.07 (ubersuggest_2018) vs 0.09 (dataforseo);
- the 14 `previsa temp…` rows of the sample add up to 125,810,310 against 96,124,520 for `previsa temp` alone.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, BG, CARD = "#111111", "#5c5c5c", "#fdfdfc", "#ffffff"
BLUE, RED = "#2f6fdb", "#d64545"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

PATTERNS = [  # (pattern, leading search, distinct searches, monthly volume)
    ("previsa temp", "previsão do tempo…", 92_914, 96_124_520),
    ("baix music", "baixar música…", 31_274, 5_578_500),
    ("fras par", "frases para…", 55_131, 8_394_870),
    ("com tir", "como tirar…", 55_495, 6_141_800),
    ("letr music", "letras de músicas…", 33_373, 3_333_860),
    ("com faz", "como fazer…", 402_509, 32_282_210),
    ("cas par", "casas para…", 71_094, 5_243_010),
    ("quant cust", "quanto custa…", 69_870, 4_544_280),
    ("ond compr", "onde comprar…", 68_672, 1_951_270),
]


def fmt(n, pt):
    s = f"{n:,.0f}"
    return s.replace(",", ".") if pt else s


def chart():
    T = {"": ("A big niche is not big everywhere", "Monthly searches per distinct search, in nine of the largest Brazilian patterns of SuperNichos",
              "searches"),
         ".pt-BR": ("Um nicho grande não é grande por inteiro", "Buscas por mês para cada busca distinta, em nove dos maiores padrões brasileiros do SuperNichos",
                    "buscas")}
    for suf, (t, s, w) in T.items():
        pt = bool(suf)
        fig = plt.figure(figsize=(11.5, 4.9), dpi=110)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0.24, 0.05, 0.6, 0.72])
        ax.set_facecolor(BG)
        fig.text(0.02, 0.95, t, fontsize=16, weight="bold", color=INK, va="top")
        fig.text(0.02, 0.885, s, fontsize=10.5, color=MUTED, va="top")
        mx = max(v / n for _, _, n, v in PATTERNS)
        for i, (_, lead, n, v) in enumerate(PATTERNS):
            y = len(PATTERNS) - 1 - i
            per = v / n
            ax.barh(y, per, color=BLUE if i == 0 else "#8fb0ea", height=0.62)
            ax.text(per + mx * 0.012, y, fmt(per, pt), va="center", color=INK, fontsize=10.5, weight="bold")
            ax.text(-mx * 0.015, y, lead, va="center", ha="right", color=INK, fontsize=11)
            ax.text(mx * 1.42, y, f"{fmt(n, pt)} {w}", va="center", ha="right", color=MUTED, fontsize=10)
        ax.set_xlim(0, mx * 1.42)
        ax.set_ylim(-0.6, len(PATTERNS) - 0.4)
        ax.axis("off")
        fig.savefig(OUT / f"per-search{suf}.png", facecolor=BG)
        plt.close(fig)


def cover():
    C = {"": ("What I learned squeezing 50 million searches",
              "The 2023 spreadsheet that became SuperNichos, how it was validated, and three numbers it got wrong",
              [("+31%", "volume counted twice in\nnested patterns"), ("41%", "of the 2018 rows: a zero\nmeant \"no data\""),
               ("×12", "CPC between two sources\nin one column")]),
         ".pt-BR": ("O que aprendi debulhando 50 milhões de buscas",
                    "A planilha de 2023 que virou o SuperNichos, como ela foi validada e três números que ela errou",
                    [("+31%", "de volume contado duas vezes\nem padrões aninhados"), ("41%", "das linhas de 2018: zero\nqueria dizer \"sem dado\""),
                     ("×12", "de CPC entre duas fontes\nna mesma coluna")])}
    for suf, (t, s, cards) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, t, fontsize=30, weight="bold", color=INK, va="top")
        ax.text(6, 50, s, fontsize=14, color=MUTED, va="center")
        for k, (big, small) in enumerate(cards):
            x = 6 + k * 43.3
            ax.add_patch(FancyBboxPatch((x, 9), 41, 30, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=RED, lw=2))
            ax.text(x + 3.5, 29, big, fontsize=34, weight="bold", color=RED, va="center")
            ax.text(x + 3.5, 19, small, fontsize=13, color=INK, va="center", linespacing=1.35)
        ax.text(6, 2.8, "github.com/CaiqueDourado/google-keywords-dataset", fontsize=11, color=MUTED)
        ax.text(134, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover()
    chart()
