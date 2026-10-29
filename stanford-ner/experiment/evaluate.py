"""Score the dictionary, the CRF and both on the two test sets (exact spans, like Stanford's own scorer).
Run after the CRF has labelled the test files (see run.sh)."""
import json, unicodedata, sys
def fold(s): return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
B = [b.split() for b in json.load(open("train_brands.json"))["train_brands"]]
import re
TOK = re.compile(r"\w+(?:[-'.]\w+)*|[^\w\s]", re.U)
BT = sorted({tuple(fold(t) for t in TOK.findall(" ".join(b))) for b in B}, key=len, reverse=True)
def sents(fn):
    out, cur = [], []
    for line in open(fn, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            if cur: out.append(cur); cur = []
            continue
        p = line.split("\t"); cur.append(p)
    if cur: out.append(cur)
    return out
def spans(labels):
    s, i = set(), 0
    while i < len(labels):
        if labels[i] != "O":
            j = i
            while j < len(labels) and labels[j] != "O": j += 1
            s.add((i, j)); i = j
        else: i += 1
    return s
def dict_lab(words):
    f = [fold(w) for w in words]; lab = ["O"] * len(words); i = 0
    while i < len(words):
        for bt in BT:
            if tuple(f[i:i+len(bt)]) == bt:
                for j in range(i, i+len(bt)): lab[j] = "MARCA"
                i += len(bt) - 1; break
        i += 1
    return lab
def score(pairs):
    tp = fp = fn = 0
    for g, p in pairs:
        G, P = spans(g), spans(p); tp += len(G & P); fp += len(P - G); fn += len(G - P)
    pr = tp / (tp + fp) if tp + fp else 0; rc = tp / (tp + fn)
    return dict(P=round(pr, 3), R=round(rc, 3), F1=round(2*pr*rc/(pr+rc), 3) if pr+rc else 0, TP=tp, FP=fp, FN=fn)
if __name__ == "__main__":
    res = {}
    for t in ("test_seen", "test_unseen"):
        S = sents(t + ".out")
        words = [[x[0] for x in s] for s in S]; gold = [[x[1] for x in s] for s in S]; crf = [[x[2] for x in s] for s in S]
        dic = [dict_lab(w) for w in words]
        both = [[("MARCA" if a != "O" or b != "O" else "O") for a, b in zip(d, c)] for d, c in zip(dic, crf)]
        res[t] = {"sentences": len(S), "dictionary": score(zip(gold, dic)), "crf": score(zip(gold, crf)), "dictionary+crf": score(zip(gold, both))}
    print(json.dumps(res, indent=1))
    json.dump(res, open("results.json", "w"), indent=1)
