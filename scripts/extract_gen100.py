#!/usr/bin/env python3
#Extract rows with gen==100 from the summary CSVs
#Writes output/CSVresults/evolving_gen100.csv and output/CSVresults/fixed_gen100.csv

import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_ROOT = os.path.join(ROOT, 'output', 'CSVresults')

FILES = {
    'evolving': os.path.join(CSV_ROOT, 'evolving_summary.csv'),
    'fixed': os.path.join(CSV_ROOT, 'fixed_summary.csv'),
}

OUTS = {
    'evolving': os.path.join(CSV_ROOT, 'evolving_gen100.csv'),
    'fixed': os.path.join(CSV_ROOT, 'fixed_gen100.csv'),
}

for mode, path in FILES.items():
    if not os.path.exists(path):
        print(f"Summary file not found: {path}")
        continue
    df = pd.read_csv(path)
    if 'gen' not in df.columns:
        print(f"No 'gen' column in {path}")
        continue
    df100 = df[df['gen'] == 100]
    df100.to_csv(OUTS[mode], index=False)
    print(f"Wrote {OUTS[mode]} rows={len(df100)}")
