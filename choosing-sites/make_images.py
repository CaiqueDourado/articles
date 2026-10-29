"""Images of part 3 (EN and PT): cover, sites per year, and the curation screen recreated with public data.

    python make_images.py --sites projetos_sites.csv --patterns padroes_algoritmos_sample.csv

projetos_sites.csv: the 83 sites (id, name, creation_date). padroes_algoritmos_sample.csv: the public sample of
google-keywords-dataset (github.com/CaiqueDourado/google-keywords-dataset/tree/main/sample).
The screen needs playwright (python -m playwright install chromium).
"""
import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "img"
INK, MUTED, LINE, BG, CARD = "#111111", "#5c5c5c", "#d9dde3", "#fdfdfc", "#ffffff"
COLORS = {"catalog": "#2a78d6", "niche": "#1baf7a", "apps": "#7c5cd6", "vehicles": "#eb6834"}
for fam in ("Inter", "DejaVu Sans"):
    try:
        matplotlib.font_manager.findfont(fam, fallback_to_default=False)
        plt.rcParams["font.family"] = fam
        break
    except ValueError:
        pass

NICHE = {1, 2, 3, 54, 61, 62, 63, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83}
APPS = {14, 15, 55, 56, 57, 58, 59, 60, 64, 65, 66}
VEHICLES = {68, 69, 70, 71}
GROUPS = {"": {"niche": "search niches (from the patterns)", "catalog": "product categories (from the catalog)",
               "apps": "apps and international (public dumps)", "vehicles": "vehicles (FIPE data)"},
          ".pt-BR": {"niche": "nichos de busca (dos padrões)", "catalog": "categorias de produto (do catálogo)",
                     "apps": "apps e internacionais (dumps públicos)", "vehicles": "veículos (dados da FIPE)"}}


def group(i):
    return "niche" if i in NICHE else "apps" if i in APPS else "vehicles" if i in VEHICLES else "catalog"


def sites_chart(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    c = Counter((r["creation_date"][:4], group(int(r["id"]))) for r in rows)
    years = sorted({y for y, _ in c})
    T = {"": ("83 sites, by year and by where they came from", "Year each site was registered in the project table (2019–2024)"),
         ".pt-BR": ("83 sites, por ano e por origem", "Ano em que cada site entrou na tabela de projetos (2019–2024)")}
    for suf, (t, s) in T.items():
        fig, ax = plt.subplots(figsize=(11, 5.4), dpi=110)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        bottom = [0] * len(years)
        for g in ("niche", "catalog", "apps", "vehicles"):
            vals = [c.get((y, g), 0) for y in years]
            ax.bar(years, vals, bottom=bottom, color=COLORS[g], width=0.62, label=GROUPS[suf][g])
            bottom = [b + v for b, v in zip(bottom, vals)]
        for x, b in zip(years, bottom):
            ax.text(x, b + 0.8, str(b), ha="center", fontsize=11, weight="bold", color=INK)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.spines["bottom"].set_color(LINE)
        ax.yaxis.set_visible(False)
        ax.tick_params(colors=INK, labelsize=11, length=0)
        ax.legend(frameon=False, fontsize=10, loc="upper left")
        fig.text(0.02, 0.94, t, fontsize=17, weight="bold", color=INK)
        fig.text(0.02, 0.895, s, fontsize=10.5, color=MUTED)
        fig.subplots_adjust(left=0.04, right=0.98, top=0.84, bottom=0.08)
        fig.savefig(OUT / f"sites{suf}.png", facecolor=BG)
        plt.close(fig)


def cover():
    C = {"": ("From 1.7 million search patterns to 83 sites:\nhow I chose what to build",
              "The curation screens, the niches I dropped, and one SQL template for 43 niche studies", "part 3 of 3"),
         ".pt-BR": ("De 1,7 milhão de padrões de busca a 83 sites:\ncomo escolhi o que construir",
                    "As telas de curadoria, os nichos que descartei e um template SQL para 43 estudos de nicho", "parte 3 de 3")}
    chips = [("previsa temp", "#d64545"), ("baix music", "#d64545"), ("result [loterias]", "#d64545"),
             ("fras par", "#1baf7a"), ("prec [produto]", "#1baf7a"), ("signific nom", "#1baf7a")]
    for suf, (title, sub, part) in C.items():
        fig = plt.figure(figsize=(14, 7.35), dpi=100)
        fig.patch.set_facecolor(BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 140)
        ax.set_ylim(0, 73.5)
        ax.axis("off")
        ax.text(6, 62, title, fontsize=29, weight="bold", color=INK, va="top", linespacing=1.15)
        ax.text(6, 43.5, sub, fontsize=14, color=MUTED, va="center")
        for i, (p, col) in enumerate(chips):
            x, y = 6 + (i % 3) * 44, 28 - (i // 3) * 13
            ax.add_patch(FancyBboxPatch((x, y - 4.5), 40, 9, boxstyle="round,pad=0,rounding_size=1.5", fc=CARD, ec=col, lw=2))
            mark = "✗" if col == "#d64545" else "✓"
            ax.text(x + 2.5, y, f"{mark}  {p}", fontsize=15, color=col, va="center", family="DejaVu Sans Mono", weight="bold")
        ax.text(6, 2.8, "github.com/CaiqueDourado/articles", fontsize=11, color=MUTED)
        ax.text(134, 2.8, part, fontsize=11, color=MUTED, ha="right")
        fig.savefig(OUT / f"cover{suf}.png", facecolor=BG)
        plt.close(fig)


def ntile(values, reverse):
    """NTILE(20) like SQL Server: sorted, first n % 20 bands one row bigger."""
    order = sorted(range(len(values)), key=lambda i: values[i], reverse=reverse)
    n = len(values)
    base, extra = divmod(n, 20)
    bands, pos = [0] * n, 0
    for b in range(20):
        size = base + (1 if b < extra else 0)
        for i in order[pos:pos + size]:
            bands[i] = b + 1
        pos += size
    return bands


def colour(band):
    """Excel's green-yellow-red scale: band 1 green, 20 red."""
    g, y, r = (99, 190, 123), (255, 235, 132), (248, 105, 107)
    t = (band - 1) / 19
    a, b, u = (g, y, t * 2) if t <= 0.5 else (y, r, (t - 0.5) * 2)
    return "#%02x%02x%02x" % tuple(round(a[k] + (b[k] - a[k]) * u) for k in range(3))


# the blacklist of the 2019 screens, by theme: weather, music and video downloads, dubbed films, lotteries and the
# animal game, football clubs (matched here on the leading search)
BLACKLIST = ("previsão do tempo", "baixar", "download", "filme", "bicho", "quina", "mega sena", "loteria", "deu no poste",
             "globo esporte", "brasileirão", "copa do mundo", "futebol")


def screen(path):
    from playwright.sync_api import sync_playwright
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["rotulos_uso"]]
    vol = [float(r["volume_total"] or 0) for r in rows]
    comp = [float(r["concorrencia_media"] or 0) for r in rows]
    cpc = [float(r["cpc_medio"] or 0) for r in rows]
    nb = [int(r["num_buscas"] or 0) for r in rows]
    bv, bc, bp, bn = ntile(vol, True), ntile(comp, False), ntile(cpc, False), ntile(nb, True)
    order = sorted(range(len(rows)), key=lambda i: -vol[i])
    pick = [i for i in order if not rows[i]["busca_lider"].startswith("´")][:22]
    H = {"": ("Curation screen, recreated", "430 labelled patterns of the public sample, biggest volume first. Each measure is cut into 20 bands (1 = best).",
              ["pattern", "leading search", "searches", "volume", "comp.", "CPC", "sum of bands", "labels"], "grey = blacklisted"),
         ".pt-BR": ("Tela de curadoria, recriada", "430 padrões rotulados da amostra pública, maior volume primeiro. Cada medida em 20 faixas (1 = melhor).",
                    ["padrão", "busca líder", "buscas", "volume", "conc.", "CPC", "soma das faixas", "rótulos"], "cinza = na blacklist")}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(device_scale_factor=2, viewport={"width": 1300, "height": 900})
        for suf, (t, s, cols, legend) in H.items():
            pt = bool(suf)
            trs = []
            for i in pick:
                r = rows[i]
                black = any(b in r["busca_lider"].lower() for b in BLACKLIST)
                fmt = (lambda v: f"{v:,.0f}".replace(",", ".")) if pt else (lambda v: f"{v:,.0f}")
                dec = (lambda v: f"{v:.2f}".replace(".", ",")) if pt else (lambda v: f"{v:.2f}")
                soma = bv[i] + bc[i] + bp[i] + bn[i]
                cls = ' class="bl"' if black else ""
                trs.append(f"<tr{cls}><td class=p>{r['padrao']}</td><td>{r['busca_lider']}</td>"
                           f"<td class=n style='background:{colour(bn[i])}'>{fmt(nb[i])}</td>"
                           f"<td class=n style='background:{colour(bv[i])}'>{fmt(vol[i])}</td>"
                           f"<td class=n style='background:{colour(bc[i])}'>{dec(comp[i])}</td>"
                           f"<td class=n style='background:{colour(bp[i])}'>{dec(cpc[i])}</td>"
                           f"<td class=n>{soma}</td><td class=l>{r['rotulos_uso']}</td></tr>")
            html = f"""<!doctype html><html><head><meta charset=utf-8><style>
body{{margin:0;background:#fdfdfc;font-family:Inter,'DejaVu Sans',sans-serif;color:#111}}
.w{{padding:24px 28px;width:1240px}} h1{{font-size:22px;margin:0 0 4px}} .s{{color:#5c5c5c;font-size:13px;margin-bottom:14px}}
table{{border-collapse:collapse;width:100%;background:#fff;border:1px solid #d9dde3;font-size:12.5px}}
th{{text-align:left;background:#f3f4f6;padding:7px 8px;font-weight:600;border-bottom:1px solid #d9dde3}}
td{{padding:5px 8px;border-top:1px solid #eef0f3;white-space:nowrap;max-width:330px;overflow:hidden;text-overflow:ellipsis}}
.p{{font-family:'DejaVu Sans Mono',monospace;font-weight:600}} .n{{text-align:right;font-variant-numeric:tabular-nums}}
.l{{color:#5c5c5c;font-size:11.5px}} tr.bl td{{color:#a3a9b2;opacity:.55}} .lg{{color:#5c5c5c;font-size:12px;margin-top:8px}}
</style></head><body><div class=w id=w><h1>{t}</h1><div class=s>{s}</div><table><tr>{''.join(f'<th>{c}</th>' for c in cols)}</tr>
{''.join(trs)}</table><div class=lg>{legend}</div></div></body></html>"""
            pg.set_content(html)
            pg.locator("#w").screenshot(path=str(OUT / f"screen{suf}.png"))
        br.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", required=True)
    ap.add_argument("--patterns", required=True)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    cover()
    sites_chart(a.sites)
    screen(a.patterns)
