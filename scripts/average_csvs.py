#!/usr/bin/env python3
#Average CSV results across runs per environment.

#Scans 'output/CSVresults/evolving' and 'output/CSVresults/fixed'
#Groups runs by the parent environment folder and dog count (e.g. field/20dogs).
#For each group, aligns by 'gen', averages numeric columns across runs, and writes summary CSVs to 'output/CSVresults/evolving_summary.csv' and 'output/CSVresults/fixed_summary.csv' with columns:mode,environment,dogs,gen,<averaged columns>


import os
import sys
import glob
import pandas as pd
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_ROOT = os.path.join(ROOT, 'output', 'CSVresults')
MODES = ['evolving', 'fixed']
OUT_FILES = {
    'evolving': os.path.join(CSV_ROOT, 'evolving_summary.csv'),
    'fixed': os.path.join(CSV_ROOT, 'fixed_summary.csv'),
}


def find_groups(mode):
    base = os.path.join(CSV_ROOT, mode)
    pattern = os.path.join(base, '**', 'results.csv')
    files = glob.glob(pattern, recursive=True)
    groups = defaultdict(list)
    for f in files:
        rel = os.path.relpath(f, base)
        parts = rel.split(os.sep)
        if len(parts) < 3:
            continue
        env = parts[0]
        dogs = parts[1]
        key = (env, dogs)
        groups[key].append(f)
    return groups


def average_group(file_list):
    dfs = []
    for p in file_list:
        try:
            df = pd.read_csv(p)
        except Exception:
            df = pd.read_csv(p, engine='python')
        if 'gen' not in df.columns:
            continue
        df = df.set_index('gen')
        dfs.append(df)
    if not dfs:
        return None
    concat = pd.concat(dfs, axis=1, keys=range(len(dfs)))
    means = concat.groupby(level=1, axis=1).mean()
    means = means.reset_index()
    return means


def process_mode(mode):
    groups = find_groups(mode)
    rows = []
    for (env, dogs), file_list in sorted(groups.items()):
        print(f'Processing mode={mode} env={env} dogs={dogs} runs={len(file_list)}', file=sys.stderr)
        avg_df = average_group(file_list)
        if avg_df is None:
            continue
        for _, row in avg_df.iterrows():
            rowd = {
                'mode': mode,
                'environment': env,
                'dogs': dogs,
                'gen': int(row['gen']) if not pd.isna(row['gen']) else row['gen']
            }
            for c in avg_df.columns:
                if c == 'gen':
                    continue
                rowd[c] = row[c]
            rows.append(rowd)
    if not rows:
        print(f'No data found for mode {mode}', file=sys.stderr)
        return
    out_df = pd.DataFrame(rows)
    out_path = OUT_FILES[mode]
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f'Wrote summary to {out_path}', file=sys.stderr)


if __name__ == '__main__':
    for mode in MODES:
        process_mode(mode)
    print('Done')
