"""Cover of the article on image similarity (EN and PT). Run: python make_images.py

The hashes on the cover are real: a drawn product photo saved at 1000 px (JPEG 90) and at 300 px (JPEG 60), hashed with
SimilarImageFinder. The other images of the article come from SimilarImageFinder's docs/img, made by its evaluation
scripts (evaluation/figures.py and evaluation/real_photos_figures.py).

    pip install pillow matplotlib "similar-image-finder @ git+https://github.com/CaiqueDourado/SimilarImageFinder#subdirectory=python"
"""
import io
from pathlib import Path

import matplotlib
from PIL import Image, ImageDraw
from similar_image_finder import exact_signature, load_gray, perceptual_hash

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, LINE, BG, CARD, GREEN, RED = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff", "#1baf7a", "#d64545"
MONO = "DejaVu Sans Mono"
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass


def photo():
    im = Image.new("RGB", (1000, 1000), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([400, 300, 600, 850], fill=(90, 50, 140))
    d.rectangle([450, 180, 550, 300], fill=(70, 40, 110))
    d.rectangle([400, 500, 600, 620], fill=(215, 140, 140))
    d.ellipse([120, 120, 170, 170], fill=(210, 120, 120))
    a, b = io.BytesIO(), io.BytesIO()
    im.save(a, "JPEG", quality=90)
    im.resize((300, 300)).save(b, "JPEG", quality=60)
    return load_gray(a.getvalue()), load_gray(b.getvalue())


def cover():
    big, small = photo()
    ha, hb = perceptual_hash(big), perceptual_hash(small)
    sa, sb = str(exact_signature(big)), str(exact_signature(small))
    C = {"": ("Finding the same photo across 7,179 stores",
              "Perceptual hashing on product photos, the hash that changed on AWS, and why 64 bits were not enough",
              "same photo, 1000 px and 300 px", f"pHash: {ha - hb} of 64 bits differ", "SHA-256: nothing in common"),
         ".pt-BR": ("Achando a mesma foto em 7.179 lojas",
                    "Hash perceptual em fotos de produto, o hash que mudou na AWS e por que 64 bits não bastaram",
                    "a mesma foto, 1000 px e 300 px", f"pHash: {ha - hb} de 64 bits diferentes", "SHA-256: nada em comum")}
    for suf, (t, s, lab, lp, ls) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, t, fontsize=31, weight="bold", color=INK, va="top")
        ax.text(6, 51, s, fontsize=14, color=MUTED, va="center")
        ax.text(6, 41, lab, fontsize=12, color=MUTED)
        for k, (lbl, a, b, col) in enumerate([(lp, str(ha), str(hb), GREEN), (ls, sa[:32] + "…", sb[:32] + "…", RED)]):
            y = 30 - k * 14
            ax.add_patch(FancyBboxPatch((6, y - 6), 128, 12, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=col, lw=2))
            ax.text(9, y + 2.4, a, fontsize=15, color=INK, family=MONO, va="center")
            ax.text(9, y - 2.6, b, fontsize=15, color=INK, family=MONO, va="center")
            ax.text(131, y, lbl, fontsize=14, color=col, va="center", ha="right", weight="bold")
        ax.text(6, 2.8, "github.com/CaiqueDourado/SimilarImageFinder", fontsize=11, color=MUTED)
        ax.text(134, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover()
