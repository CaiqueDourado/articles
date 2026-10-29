"""Images of the article on Stanford NER (EN and PT): cover and results chart. Run: python make_images.py

Numbers from experiment/results.json (experiment/run.sh: Stanford NER 3.9.1, the 2018 properties file, product names of
brazilian-ecommerce-products/sample labelled with their own brand).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
R = json.loads((HERE / "experiment" / "results.json").read_text())
INK, MUTED, BG, CARD = "#111111", "#5c5c5c", "#fdfdfc", "#ffffff"
GREY, BLUE, GREEN = "#9aa1ab", "#2f6fdb", "#1baf7a"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass


def pc(v, pt):
    s = f"{100 * v:.1f}%"
    return s.replace(".", ",") if pt else s


def chart():
    T = {"": ("The dictionary knows what it knows. The model guesses the rest.",
              "Brands found in product names, exact span; test names with brands seen in training vs never seen",
              ("brands seen in training", "brands never seen"), ("dictionary", "CRF model"), ("found (recall)", "right (precision)")),
         ".pt-BR": ("O dicionário sabe o que sabe. O modelo chuta o resto.",
                    "Marcas achadas em nomes de produtos, trecho exato; nomes com marcas vistas no treino e nunca vistas",
                    ("marcas vistas no treino", "marcas nunca vistas"), ("dicionário", "modelo CRF"), ("achadas (revocação)", "certas (precisão)"))}
    for suf, (t, s, groups, methods, metrics) in T.items():
        pt = bool(suf)
        fig = plt.figure(figsize=(11.5, 4.8), dpi=110)
        fig.patch.set_facecolor(BG)
        fig.text(0.02, 0.95, t, fontsize=16, weight="bold", color=INK, va="top")
        fig.text(0.02, 0.885, s, fontsize=10.5, color=MUTED, va="top")
        for k, key in enumerate(("test_seen", "test_unseen")):
            ax = fig.add_axes([0.06 + k * 0.48, 0.1, 0.42, 0.58])
            ax.set_facecolor(BG)
            ax.set_title(groups[k], fontsize=12, color=INK, loc="left", weight="bold")
            for i, (m, col) in enumerate((("dictionary", GREY), ("crf", BLUE))):
                for j, met in enumerate(("R", "P")):
                    x = j * 3 + i
                    v = R[key][m][met]
                    ax.bar(x, v, color=col, width=0.85)
                    ax.text(x, v + 0.02, pc(v, pt), ha="center", fontsize=10.5, weight="bold", color=INK)
            ax.set_xticks([0.5, 3.5], metrics, fontsize=10.5)
            ax.set_ylim(0, 1.12)
            ax.set_yticks([])
            for sp in ("top", "right", "left"):
                ax.spines[sp].set_visible(False)
        fig.legend(handles=[Patch(color=GREY, label=methods[0]), Patch(color=BLUE, label=methods[1])], frameon=False,
                   loc="upper right", bbox_to_anchor=(0.98, 0.9), ncol=2, fontsize=10.5)
        fig.savefig(OUT / f"results{suf}.png", facecolor=BG)
        plt.close(fig)


def cover():
    u = R["test_unseen"]
    C = {"": ("Training Stanford NER on Portuguese with a dictionary", "My 2018 notes, and a 2026 rerun that measures what the model learns beyond the list",
              "Brands the model never saw", f"dictionary: {pc(u['dictionary']['R'], False)} found", f"CRF model: {pc(u['crf']['R'], False)} found"),
         ".pt-BR": ("Treinando o Stanford NER em português com um dicionário", "Minhas anotações de 2018, e uma reexecução em 2026 que mede o que o modelo aprende além da lista",
                    "Marcas que o modelo nunca viu", f"dicionário: {pc(u['dictionary']['R'], True)} achadas", f"modelo CRF: {pc(u['crf']['R'], True)} achadas")}
    sample = [("Guarda Roupa Casal 6 Portas - ", "Leifer"), ("Saleiro Plástico Decorado 1L - ", "Plasutil")]
    for suf, (t, s, lab, d, m) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 63, t, fontsize=28, weight="bold", color=INK, va="top")
        ax.text(6, 52, s, fontsize=14, color=MUTED, va="center")
        ax.add_patch(FancyBboxPatch((6, 9), 128, 33, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=BLUE, lw=2))
        ax.text(10, 37, lab, fontsize=13, weight="bold", color=BLUE, va="center")
        for i, (a, b) in enumerate(sample):
            y = 29 - i * 6
            ax.text(10, y, a, fontsize=14, color=INK, va="center", family="DejaVu Sans Mono")
            ax.text(10 + len(a) * 1.18, y, b, fontsize=14, color="white", va="center", family="DejaVu Sans Mono",
                    bbox=dict(boxstyle="round,pad=0.25", fc=BLUE, ec=BLUE))
            ax.text(10 + (len(a) + len(b)) * 1.18 + 3, y, "MARCA", fontsize=11, color=BLUE, va="center", weight="bold")
        ax.text(10, 14, d, fontsize=14, color=MUTED, va="center")
        ax.text(70, 14, m, fontsize=14, color=BLUE, va="center", weight="bold")
        ax.text(6, 2.8, "nlp.stanford.edu/software/CRF-NER.html", fontsize=11, color=MUTED)
        ax.text(134, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover()
    chart()
