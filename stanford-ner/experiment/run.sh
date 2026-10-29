#!/usr/bin/env bash
# Rerun of the 2018 Stanford NER training on public data (2026).
# Needs Java and Stanford NER 3.9.1 (stanford-ner-2018-02-27.zip, https://nlp.stanford.edu/software/CRF-NER.html),
# and sample/produtos.csv from https://github.com/CaiqueDourado/brazilian-ecommerce-products.
set -euo pipefail
JAR=${JAR:-stanford-ner-2018-02-27/stanford-ner.jar}
PRODUTOS=${PRODUTOS:-brazilian-ecommerce-products/sample/produtos.csv}
pip install duckdb
python prep.py "$PRODUTOS"                       # train.tsv, test_seen.tsv, test_unseen.tsv, train_brands.json
java -mx2g -cp "$JAR" edu.stanford.nlp.ie.crf.CRFClassifier -prop marca.props        # marca.ser.gz
for t in test_seen test_unseen; do
  java -mx2g -cp "$JAR" edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier marca.ser.gz \
       -testFile $t.tsv -outputEncoding UTF-8 > $t.out
done
python evaluate.py                                # results.json
