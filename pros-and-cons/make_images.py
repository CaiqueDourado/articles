"""Images of the article on pros and cons (EN and PT): cover and the cons chart. Run: python make_images.py

Numbers from pros-e-contras-ptbr, evaluation/results/summary.json (51 held-out products, 204 listed clauses per side).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, LINE, BG, CARD = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff"
GREEN, RED, GREY = "#1baf7a", "#d64545", "#b9bec5"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

RESULTS = [  # (label EN, label PT, right, wrong side, no opinion)
    ("cons, 2020", "contras, 2020", 64.7, 9.3, 26.0),
    ("cons, 2026", "contras, 2026", 89.7, 2.5, 7.8),
    ("pros, 2020", "prós, 2020", 97.1, 0.5, 2.5),
    ("pros, 2026", "prós, 2026", 99.5, 0.0, 0.5),
]


def chart():
    T = {"": ("The cons were where the 2020 method failed", "Share of the listed clauses, 51 products held out of training, 204 clauses per row",
              ("right", "wrong side", "no opinion")),
         ".pt-BR": ("Os contras eram onde o método de 2020 falhava", "Parte das frases listadas, 51 produtos fora do treino, 204 frases por linha",
                    ("certo", "lado errado", "sem opinião"))}
    for suf, (t, s, legend) in T.items():
        pt = bool(suf)
        fig = plt.figure(figsize=(11.5, 4.4), dpi=110)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0.16, 0.08, 0.8, 0.62])
        ax.set_facecolor(BG)
        fig.text(0.02, 0.95, t, fontsize=16, weight="bold", color=INK, va="top")
        fig.text(0.02, 0.885, s, fontsize=10.5, color=MUTED, va="top")
        for i, (en, ptl, r, w, n) in enumerate(RESULTS):
            y = len(RESULTS) - 1 - i
            left = 0
            for v, c in ((r, GREEN), (w, RED), (n, GREY)):
                ax.barh(y, v, left=left, color=c, height=0.62)
                left += v
            ax.text(1.5, y, (f"{r:.1f}%".replace(".", ",") if pt else f"{r:.1f}%"), va="center", color="white", fontsize=10.5, weight="bold")
            ax.text(-1.5, y, ptl if pt else en, va="center", ha="right", color=INK, fontsize=11)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.6, len(RESULTS) - 0.4)
        ax.axis("off")
        ax.legend(handles=[Patch(color=c, label=l) for c, l in zip((GREEN, RED, GREY), legend)], frameon=False, fontsize=10,
                  loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3)
        fig.savefig(OUT / f"results{suf}.png", facecolor=BG)
        plt.close(fig)


def cover():
    C = {"": ("Sentence splitting + sentiment analysis\n= pros and cons", "What the 2020 formula got wrong on 2.87 million Brazilian reviews, and the fix",
              "Pros", "Cons", "2020", "2026"),
         ".pt-BR": ("Divisão de sentenças + análise de\nsentimentos = prós e contras", "O que a fórmula de 2020 errou em 2,87 milhões de avaliações brasileiras, e a correção",
                    "Prós", "Contras", "2020", "2026")}
    before = ["No mais", "Ainda assim", "O box", "Desta forma"]
    after = ["Rasga a toa", "…ter vindo com defeito", "A capa do box veio rasgada"]
    for suf, (t, s, _, cons, y0, y1) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 63, t, fontsize=29, weight="bold", color=INK, va="top", linespacing=1.15)
        ax.text(6, 44, s, fontsize=14, color=MUTED, va="center")
        for k, (yr, items, col) in enumerate(((y0, before, RED), (y1, after, GREEN))):
            x = 6 + k * 66
            ax.add_patch(FancyBboxPatch((x, 7), 62, 29, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=col, lw=2))
            ax.text(x + 3, 32, f"{cons} · {yr}", fontsize=13, weight="bold", color=col, va="center")
            for i, it in enumerate(items):
                ax.text(x + 3, 26 - i * 4.8, it, fontsize=13, color=INK, va="center", family="DejaVu Sans Mono")
        ax.text(6, 2.8, "github.com/CaiqueDourado/pros-e-contras-ptbr", fontsize=11, color=MUTED)
        ax.text(134, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover()
    chart()
