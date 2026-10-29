"""Images of the article on enriching sign-up data with open APIs (EN and PT): cover and the coverage chart.
Run: python make_images.py

The cover numbers are real answers of the IBGE names API for "Caique" (v1 basica with sexo=F and sexo=M; v2 by sex).
The chart is computed from brazilian-names-surnames, data/nomes.parquet: first names of the 24,771,272 company
partners in the CNPJ register, weighted by `cnpj_partners`:

    SELECT sum(cnpj_partners) FILTER (WHERE ibge_frequency IS NOT NULL),
           sum(cnpj_partners) FILTER (WHERE ibge_share_female IS NOT NULL),
           sum(cnpj_partners) FILTER (WHERE ibge_share_female >= 0.9 OR ibge_share_female <= 0.1),
           sum(cnpj_partners) FILTER (WHERE ibge_share_female BETWEEN 0.1 AND 0.9),
           sum(cnpj_partners)
    FROM 'data/nomes.parquet'

by_decade*.png is copied from ibge-nomes (tools/make_figure.py).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, BG, CARD = "#111111", "#5c5c5c", "#fdfdfc", "#ffffff"
GREEN, RED, BLUE, GREY = "#1baf7a", "#d64545", "#2f6fdb", "#b9bec5"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

TOTAL = 24_771_272
COVERAGE = [  # (EN, PT, partners, colour)
    ("first name is in the 2010 Census", "o primeiro nome está no Censo 2010", 24_340_378, BLUE),
    ("IBGE publishes women and men for it", "o IBGE publica mulheres e homens", 24_129_031, BLUE),
    ("90% or more of one sex", "90% ou mais de um sexo", 23_828_990, GREEN),
    ("between 10% and 90% women", "entre 10% e 90% de mulheres", 300_095, RED),
]


def pct(v, pt):
    s = f"{100 * v / TOTAL:.1f}%"
    return s.replace(".", ",") if pt else s


def chart():
    T = {"": ("How far a first name goes", "Company partners in the CNPJ register (24.8 million people), by what IBGE knows about their first name"),
         ".pt-BR": ("Até onde vai um primeiro nome", "Sócios de empresas no cadastro do CNPJ (24,8 milhões de pessoas), pelo que o IBGE sabe do primeiro nome")}
    for suf, (t, s) in T.items():
        pt = bool(suf)
        fig = plt.figure(figsize=(11.5, 4.2), dpi=110)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0.33, 0.06, 0.6, 0.66])
        ax.set_facecolor(BG)
        fig.text(0.02, 0.95, t, fontsize=16, weight="bold", color=INK, va="top")
        fig.text(0.02, 0.875, s, fontsize=10.5, color=MUTED, va="top")
        for i, (en, ptl, v, col) in enumerate(COVERAGE):
            y = len(COVERAGE) - 1 - i
            ax.barh(y, 100, color="#eef0f3", height=0.6)
            ax.barh(y, 100 * v / TOTAL, color=col, height=0.6)
            x = 100 * v / TOTAL
            ax.text(x - 1.2 if x > 15 else x + 1.2, y, pct(v, pt), va="center", ha="right" if x > 15 else "left",
                    color="white" if x > 15 else INK, fontsize=11, weight="bold")
            ax.text(-1.5, y, ptl if pt else en, va="center", ha="right", color=INK, fontsize=11)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.6, len(COVERAGE) - 0.4)
        ax.axis("off")
        fig.savefig(OUT / f"coverage{suf}.png", facecolor=BG)
        plt.close(fig)


def cover():
    C = {"": ("Enriching sign-up data with open APIs", "Sex, generation and place from a name, a CEP and a phone, with IBGE and other free sources",
              "2018 draft: read as probability", ["women 0.7634", "men 67.6326"], "people per 100k in Bahia",
              "2026: what the numbers mean", ["1.1% women · 98.9% men", "peak: born in the 2000s", "most common in Bahia"]),
         ".pt-BR": ("Enriquecendo cadastros com APIs abertas", "Sexo, geração e lugar a partir de um nome, um CEP e um telefone, com o IBGE e outras fontes grátis",
                    "Rascunho de 2018: lido como probabilidade", ["mulheres 0,7634", "homens 67,6326"], "pessoas por 100 mil na Bahia",
                    "2026: o que os números dizem", ["1,1% mulheres · 98,9% homens", "pico: nascidos nos anos 2000", "mais comum na Bahia"])}
    for suf, (t, s, l0, it0, note0, l1, it1) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, t, fontsize=31, weight="bold", color=INK, va="top")
        ax.text(6, 51, s, fontsize=14, color=MUTED, va="center")
        ax.text(6, 43, "Caique · IBGE, Censo 2010", fontsize=12, color=MUTED, va="center")
        for k, (lab, items, col) in enumerate(((l0, it0, RED), (l1, it1, GREEN))):
            x = 6 + k * 66
            ax.add_patch(FancyBboxPatch((x, 7), 62, 31, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=col, lw=2))
            ax.text(x + 3, 34, lab, fontsize=13, weight="bold", color=col, va="center")
            for i, it in enumerate(items):
                ax.text(x + 3, 27.5 - i * 5, it, fontsize=13.5, color=INK, va="center", family="DejaVu Sans Mono")
            if k == 0:
                ax.text(x + 3, 12, "= " + note0, fontsize=12, color=MUTED, va="center", style="italic")
        ax.text(6, 2.8, "github.com/CaiqueDourado/ibge-nomes", fontsize=11, color=MUTED)
        ax.text(134, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover()
    chart()
