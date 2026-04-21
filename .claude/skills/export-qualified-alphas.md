---
description: Export qualified alphas from WQ-Brain simulation results
---

# Export Qualified Alphas

This skill analyzes all simulation results and exports qualified alphas that meet IQC submission criteria.

## Criteria

An alpha is considered qualified if it passes:
- Sharpe > 1.25
- Fitness >= 1.0
- Turnover between 1% and 70%
- Weight check: PASS

## Usage

When invoked, this skill will:
1. Scan all CSV files in `data/api_*.csv`
2. Filter alphas meeting the criteria
3. Sort by fitness (descending)
4. Output a formatted report with:
   - Alpha ID and link
   - Key metrics (sharpe, fitness, turnover)
   - Formula code
   - Parameters (decay, truncation, neutralization)

## Implementation

```python
import csv
import glob
from tabulate import tabulate

def export_qualified_alphas():
    """Export all qualified alphas from simulation results."""
    
    qualified = []
    
    for csv_file in glob.glob('/Users/jakin/GitHub/WQ-Brain/data/api_*.csv'):
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
                            'passed': row['passed'],
                            'link': row['link'],
                            'code': row['code']
                        })
                except (ValueError, KeyError):
                    continue
    
    # Sort by fitness descending
    qualified.sort(key=lambda x: x['fitness'], reverse=True)
    
    # Format output
    print(f"\n{'='*80}")
    print(f"QUALIFIED ALPHAS: {len(qualified)} found")
    print(f"{'='*80}\n")
    
    for i, alpha in enumerate(qualified, 1):
        print(f"{i}. {alpha['id']} (passed {alpha['passed']}/8)")
        print(f"   Sharpe: {alpha['sharpe']:.2f} | Fitness: {alpha['fitness']:.2f} | Turnover: {alpha['turnover']:.2f}%")
        print(f"   Params: decay={alpha['decay']}, trunc={alpha['truncation']}, neut={alpha['neutralization']}")
        print(f"   Link: {alpha['link']}")
        print(f"   Code: {alpha['code'][:100]}{'...' if len(alpha['code']) > 100 else ''}")
        print()
    
    return qualified

if __name__ == '__main__':
    export_qualified_alphas()
```

## Example Output

```
================================================================================
QUALIFIED ALPHAS: 3 found
================================================================================

1. 3qnoVpN6 (passed 7/8)
   Sharpe: 1.65 | Fitness: 1.97 | Turnover: 7.84%
   Params: decay=15, trunc=0.08, neut=SECTOR
   Link: https://platform.worldquantbrain.com/alpha/3qnoVpN6
   Code: scale(((ts_sum(close, 7) / 7) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))

2. kqLNgLgO (passed 7/8)
   Sharpe: 1.71 | Fitness: 1.89 | Turnover: 10.91%
   Params: decay=15, trunc=0.08, neut=SECTOR
   Link: https://platform.worldquantbrain.com/alpha/kqLNgLgO
   Code: scale(((ts_sum(close, 7) / 7) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))

3. j2dY8n55 (passed 7/8)
   Sharpe: 1.68 | Fitness: 1.85 | Turnover: 9.84%
   Params: decay=12, trunc=0.08, neut=SUBINDUSTRY
   Link: https://platform.worldquantbrain.com/alpha/j2dY8n55
   Code: scale(((ts_sum(close, 7) / 7) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))
```
