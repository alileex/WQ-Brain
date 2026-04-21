#!/usr/bin/env python3
"""Export qualified alphas from WQ-Brain simulation results."""

import csv
import glob
import sys

def export_qualified_alphas(data_dir='data'):
    """Export all qualified alphas from simulation results.

    Criteria:
    - Sharpe > 1.25
    - Fitness >= 1.0
    - Turnover between 1% and 70%
    - Weight check: PASS
    """

    qualified = []

    pattern = f'{data_dir}/api_*.csv'
    csv_files = glob.glob(pattern)

    if not csv_files:
        print(f"No CSV files found matching: {pattern}")
        return []

    for csv_file in csv_files:
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    sharpe = float(row['sharpe'])
                    fitness = float(row['fitness'])
                    turnover = float(row['turnover'])
                    weight = row['weight']

                    # Check qualification criteria
                    if (sharpe > 1.25 and
                        fitness >= 1.0 and
                        1.0 <= turnover <= 70.0 and
                        weight == 'PASS'):

                        alpha_id = row['link'].split('/')[-1]
                        qualified.append({
                            'id': alpha_id,
                            'sharpe': sharpe,
                            'fitness': fitness,
                            'turnover': turnover,
                            'decay': row['decay'],
                            'truncation': row['truncation'],
                            'neutralization': row['neutralization'],
                            'region': row['region'],
                            'universe': row['universe'],
                            'passed': row['passed'],
                            'subsharpe': row.get('subsharpe', '-'),
                            'link': row['link'],
                            'code': row['code']
                        })
                except (ValueError, KeyError) as e:
                    continue

    # Sort by fitness descending
    qualified.sort(key=lambda x: x['fitness'], reverse=True)

    # Format output
    print(f"\n{'='*100}")
    print(f"QUALIFIED ALPHAS: {len(qualified)} found")
    print(f"{'='*100}\n")

    if not qualified:
        print("No alphas meet the qualification criteria.")
        print("\nCriteria:")
        print("  - Sharpe > 1.25")
        print("  - Fitness >= 1.0")
        print("  - Turnover: 1% - 70%")
        print("  - Weight: PASS")
        return []

    for i, alpha in enumerate(qualified, 1):
        print(f"{i}. {alpha['id']} (passed {alpha['passed']}/8)")
        print(f"   Sharpe: {alpha['sharpe']:.2f} | Fitness: {alpha['fitness']:.2f} | Turnover: {alpha['turnover']:.2f}% | SubSharpe: {alpha['subsharpe']}")
        print(f"   Params: decay={alpha['decay']}, trunc={alpha['truncation']}, neut={alpha['neutralization']}")
        print(f"   Region: {alpha['region']}, Universe: {alpha['universe']}")
        print(f"   Link: {alpha['link']}")
        print(f"   Code: {alpha['code'][:120]}{'...' if len(alpha['code']) > 120 else ''}")
        print()

    return qualified

if __name__ == '__main__':
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    alphas = export_qualified_alphas(data_dir)

    if alphas:
        print(f"\n{'='*100}")
        print(f"Summary: {len(alphas)} qualified alphas ready for submission")
        print(f"Top 3 by fitness:")
        for i, alpha in enumerate(alphas[:3], 1):
            print(f"  {i}. {alpha['id']}: fitness={alpha['fitness']:.2f}, sharpe={alpha['sharpe']:.2f}")
        print(f"{'='*100}\n")
