"""Images of the article on text similarity (EN and PT): cover, phonetic keys, similarity scores, safeguards.

    pip install jellyfish "dedupkit-br @ git+https://github.com/CaiqueDourado/DedupKit#subdirectory=python"
    python make_images.py

Every number is computed here (phonetic keys, Jaccard and MinHash) or copied from DedupKit's evaluation/results.md.
"""
import hashlib
import re
import unicodedata
from pathlib import Path

import jellyfish
import matplotlib
from dedupkit_br import phonetic_key

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, LINE, BG, CARD = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff"
GREEN, RED, BLUE, GREY = "#1baf7a", "#d64545", "#2a78d6", "#9aa0a6"
MONO = "DejaVu Sans Mono"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def soundex(w):
    """American Soundex, as databases ship it (SQL Server SOUNDEX, for example)."""
    w = fold(w)
    codes = {**{c: "1" for c in "bfpv"}, **{c: "2" for c in "cgjkqsxz"}, **{c: "3" for c in "dt"}, "l": "4",
             **{c: "5" for c in "mn"}, "r": "6"}
    out, prev = w[0].upper(), codes.get(w[0], "")
    for c in w[1:]:
        d = codes.get(c, "")
        if d and d != prev:
            out += d
        if c not in "hw":
            prev = d
    return (out + "000")[:4]


def shingles(s, k=3):
    s = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", fold(s))).strip()
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def jaccard(a, b):
    x, y = shingles(a), shingles(b)
    return len(x & y) / len(x | y)


def minhash(a, b, n=128):
    """MinHash estimate of the Jaccard similarity with n hash functions."""
    sig = lambda s: [min(int(hashlib.md5(f"{i}:{g}".encode()).hexdigest()[:8], 16) for g in shingles(s)) for i in range(n)]  # noqa: E731
    return sum(p == q for p, q in zip(sig(a), sig(b))) / n


WORDS = [("xuveiro", "chuveiro", True), ("caçarola", "cassarola", True), ("geladeira", "jeladeira", True),
         ("hambúrguer", "hamburger", True), ("queimada", "comida", False), ("concerto", "conserto", False)]
PAIRS = [  # (a, b, same product?, why)
    ("Fone de Ouvido sem Fio JBL Tune 510BT Preto", "FONES DE OUVIDO JBL TUNE 510BT S/ FIO PRETO", True, ""),
    ("Xuveiro eletrico", "Chuveiro elétrico", True, ""),
    ("Chuveiro Elétrico Lorenzetti Acqua Duo 220V 7800W", "Chuveiro Eletrico Lorenzetti Acqua Duo 127V 5500W", False, "220 V × 127 V"),
    ("Mass Way 2500 Baunilha 400g", "Mass Way 2500 (500g) - Baunilha", False, "400 g × 500 g"),
    ("Shampoo Aussie Moist 865ML", "Shampoo Aussie Moist 180 Ml", False, "865 ml × 180 ml"),
]
SAFE = [  # DedupKit evaluation/results.md, 4,073 synthetic listings
    ("2019 catalog: every key, two hops, fingerprint bug", "Catálogo de 2019: todas as chaves, dois saltos, bug do fingerprint", 23.4, 91.2),
    ("+ fingerprint fixed, one-step clusters", "+ fingerprint corrigido, grupos de um passo", 44.4, 91.2),
    ("+ attribute check (size, voltage, colour…)", "+ checagem de atributos (tamanho, voltagem, cor…)", 81.5, 90.2),
    ("+ brand check", "+ checagem de marca", 87.6, 90.2),
]


def title(fig, t, s):
    fig.text(0.02, 0.95, t, fontsize=16, weight="bold", color=INK, va="top")
    fig.text(0.02, 0.885, s, fontsize=10.5, color=MUTED, va="top")


def phonetic():
    T = {"": ("Phonetic keys on Portuguese words", "English Soundex and Metaphone against DedupKit's Portuguese key. Green: same key. Red: same key for different words",
              ["word A", "word B", "same word?", "Soundex", "Metaphone", "DedupKit"], ("yes", "no")),
         ".pt-BR": ("Chaves fonéticas em palavras do português", "Soundex e Metaphone do inglês contra a chave em português do DedupKit. Verde: mesma chave. Vermelho: mesma chave para palavras diferentes",
                    ["palavra A", "palavra B", "mesma palavra?", "Soundex", "Metaphone", "DedupKit"], ("sim", "não"))}
    for suf, (t, s, head, yn) in T.items():
        fig = plt.figure(figsize=(11.5, 4.9), dpi=110)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 0.84])
        ax.set_xlim(0, 115)
        ax.set_ylim(0, 8)
        ax.axis("off")
        title(fig, t, s)
        xs = [2, 19, 36, 52, 73, 94]
        for x, h in zip(xs, head):
            ax.text(x, 7.3, h, fontsize=10.5, weight="bold", color=MUTED)
        for i, (a, b, same) in enumerate(WORDS):
            y = 6.2 - i
            ax.plot([1, 114], [y + 0.5, y + 0.5], color=LINE, lw=0.8)
            ax.text(xs[0], y, a, fontsize=11.5, color=INK, family=MONO, va="center")
            ax.text(xs[1], y, b, fontsize=11.5, color=INK, family=MONO, va="center")
            ax.text(xs[2], y, yn[0] if same else yn[1], fontsize=11.5, color=INK, va="center")
            for x, f in zip(xs[3:], (soundex, jellyfish.metaphone, phonetic_key)):
                ka, kb = f(fold(a) if f is jellyfish.metaphone else a), f(fold(b) if f is jellyfish.metaphone else b)
                eq = ka == kb
                col = (GREEN if same else RED) if eq else MUTED
                ax.text(x, y, f"{ka} {'=' if eq else '≠'} {kb}", fontsize=11, color=col, family=MONO, va="center",
                        weight="bold" if eq else "normal")
        fig.savefig(OUT / f"phonetic{suf}.png", facecolor=BG)
        plt.close(fig)


def scores():
    T = {"": ("A similarity score cannot tell a product from its sibling",
              "Jaccard similarity of character 3-grams and its MinHash estimate (128 hashes), on real catalog names",
              "same product", "different product", "what differs"),
         ".pt-BR": ("Uma nota de similaridade não separa o produto do irmão dele",
                    "Similaridade de Jaccard de trigramas de letras e a estimativa por MinHash (128 hashes), em nomes reais do catálogo",
                    "mesmo produto", "produto diferente", "o que muda")}
    n = len(PAIRS)
    for suf, (t, s, ls, ld, wd) in T.items():
        fig = plt.figure(figsize=(12, 6.2), dpi=110)
        fig.patch.set_facecolor(BG)
        y0, h = 0.1, 0.66
        ax = fig.add_axes([0.5, y0, 0.46, h])
        ax.set_facecolor(BG)
        title(fig, t, s)
        for i, (a, b, same, why) in enumerate(PAIRS):
            y = n - 1 - i
            j, m = jaccard(a, b), minhash(a, b)
            col = GREEN if same else RED
            ax.plot([0.5, 1], [y, y], color=LINE, lw=0.8, zorder=1)
            ax.scatter([j], [y], s=90, color=col, zorder=3)
            ax.scatter([m], [y], s=90, facecolors="none", edgecolors=col, linewidths=1.6, zorder=3)
            ax.text(max(j, m) + 0.015, y, f"{j:.2f}".replace(".", ",") if suf else f"{j:.2f}", fontsize=10, color=col, va="center")
            yy = y0 + h * (y + 0.6) / (n + 0.2)
            fig.text(0.02, yy + 0.025, a, fontsize=9, color=INK, family=MONO)
            fig.text(0.02, yy - 0.005, b, fontsize=9, color=INK, family=MONO)
            if why:
                fig.text(0.02, yy - 0.035, f"{wd}: {why}", fontsize=9, color=RED)
        ax.set_xlim(0.5, 1)
        ax.set_ylim(-0.6, n - 0.4)
        ax.yaxis.set_visible(False)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color(LINE)
        ax.tick_params(colors=MUTED, labelsize=9.5, length=0)
        ax.scatter([], [], s=70, color=GREEN, label=ls)
        ax.scatter([], [], s=70, color=RED, label=ld)
        ax.scatter([], [], s=70, facecolors="none", edgecolors=MUTED, label="MinHash")
        ax.legend(frameon=False, fontsize=9.5, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3)
        fig.savefig(OUT / f"scores{suf}.png", facecolor=BG)
        plt.close(fig)


def safeguards():
    T = {"": ("What made the matching right was not a better key", "Precision and recall on 4,073 synthetic listings with known answers (DedupKit evaluation)", "precision", "recall"),
         ".pt-BR": ("O que acertou o agrupamento não foi uma chave melhor", "Precisão e revocação em 4.073 anúncios sintéticos com resposta conhecida (avaliação do DedupKit)", "precisão", "revocação")}
    for suf, (t, s, lp, lr) in T.items():
        pt = bool(suf)
        fig = plt.figure(figsize=(11.5, 5.2), dpi=110)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0.47, 0.06, 0.5, 0.66])
        ax.set_facecolor(BG)
        title(fig, t, s)
        for i, (en, ptl, p, r) in enumerate(SAFE):
            y = len(SAFE) - 1 - i
            ax.barh(y + 0.17, p, height=0.32, color=BLUE)
            ax.barh(y - 0.17, r, height=0.32, color=GREY)
            ax.text(p + 1, y + 0.17, f"{p:.1f}%".replace(".", ",") if pt else f"{p:.1f}%", va="center", fontsize=10, color=INK, weight="bold")
            ax.text(r + 1, y - 0.17, f"{r:.1f}%".replace(".", ",") if pt else f"{r:.1f}%", va="center", fontsize=9.5, color=MUTED)
            fig.text(0.02, 0.06 + 0.66 * (y + 0.5) / len(SAFE), ptl if pt else en, fontsize=10.5, color=INK, va="center")
        ax.set_xlim(0, 110)
        ax.set_ylim(-0.6, len(SAFE) - 0.4)
        ax.axis("off")
        from matplotlib.patches import Patch
        ax.legend(handles=[Patch(color=BLUE, label=lp), Patch(color=GREY, label=lr)], frameon=False, fontsize=9.5,
                  loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
        fig.savefig(OUT / f"safeguards{suf}.png", facecolor=BG)
        plt.close(fig)


def cover():
    C = {"": ("Metaphone, Soundex, n-grams and MinHash\non Brazilian product names",
              "Similar is not the same: what each algorithm finds, and what actually decided"),
         ".pt-BR": ("Metaphone, Soundex, n-gramas e MinHash\nem nomes de produtos brasileiros",
                    "Parecido não é igual: o que cada algoritmo encontra e o que de fato decidiu")}
    rows = [("Fone de Ouvido sem Fio JBL Tune 510BT Preto", "FONES DE OUVIDO JBL TUNE 510BT S/ FIO PRETO", "✓", GREEN),
            ("Chuveiro Lorenzetti Acqua Duo 220V 7800W", "Chuveiro Lorenzetti Acqua Duo 127V 5500W", "✗", RED)]
    for suf, (t, s) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, t, fontsize=30, weight="bold", color=INK, va="top", linespacing=1.15)
        ax.text(6, 43.5, s, fontsize=14, color=MUTED, va="center")
        for k, (a, b, mark, col) in enumerate(rows):
            y = 30 - k * 13
            ax.add_patch(FancyBboxPatch((6, y - 5.5), 128, 11, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=col, lw=2))
            ax.text(9, y + 2, a, fontsize=12.5, color=INK, family=MONO, va="center")
            ax.text(9, y - 2.6, b, fontsize=12.5, color=INK, family=MONO, va="center")
            ax.text(128, y, mark, fontsize=26, color=col, va="center", ha="center", weight="bold")
        ax.text(6, 2.8, "github.com/CaiqueDourado/DedupKit", fontsize=11, color=MUTED)
        ax.text(134, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover()
    phonetic()
    scores()
    safeguards()
    for a, b, same, _ in PAIRS:
        print(f"{jaccard(a, b):.2f} {minhash(a, b):.2f} {same} {a} × {b}")
