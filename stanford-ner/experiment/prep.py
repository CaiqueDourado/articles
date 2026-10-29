"""Build Stanford NER training and test files: product names labelled with their own brand.

Silver labels: the brand comes from the store's brand field and is marked wherever it appears in the name.
Brands are split 80/20, so test_unseen has only brands the model never saw. Usage: python prep.py produtos.csv
"""
import random, re, unicodedata, duckdb, json, sys
SRC = sys.argv[1]
BAD = {"não informado","nao informado","indisponível","indisponivel","genérico","generico","generica","genérica","outros","outras","sem marca","diversos","diversas","importado","importada","n/a","na","-"}
def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
TOK = re.compile(r"\w+(?:[-'.]\w+)*|[^\w\s]", re.U)
rows = duckdb.sql(f"select distinct name, brand from '{SRC}' where brand<>'' and name<>'' order by name, brand").fetchall()
data = {}
for name, brand in rows:
    b = brand.strip()
    if fold(b) in BAD or len(b) < 2: continue
    toks = TOK.findall(name); btoks = [fold(t) for t in TOK.findall(b)]
    ft = [fold(t) for t in toks]; n = len(btoks)
    lab = ["O"] * len(toks); hit = False
    for i in range(len(toks) - n + 1):
        if ft[i:i+n] == btoks:
            for j in range(i, i+n): lab[j] = "MARCA"
            hit = True
    if hit and name not in data:
        data[name] = (fold(b), toks, lab)
brands = sorted({v[0] for v in data.values()})
random.seed(7); random.shuffle(brands)
cut = int(len(brands) * 0.8); train_b = set(brands[:cut])
train = sorted((v for v in data.values() if v[0] in train_b), key=lambda v: " ".join(v[1]))
unseen = sorted((v for v in data.values() if v[0] not in train_b), key=lambda v: " ".join(v[1]))
random.shuffle(train)
k = len(train) // 5
seen_test, train = train[:k], train[k:]
def write(fn, items):
    with open(fn, "w", encoding="utf-8") as f:
        for _, toks, lab in items:
            for t, l in zip(toks, lab): f.write(f"{t}\t{l}\n")
            f.write("\n")
write("train.tsv", train); write("test_seen.tsv", seen_test); write("test_unseen.tsv", unseen)
json.dump({"train_brands": sorted(train_b)}, open("train_brands.json", "w"))
print(json.dumps({"names": len(data), "brands": len(brands), "train_brands": len(train_b), "train": len(train), "test_seen": len(seen_test), "test_unseen": len(unseen)}))
