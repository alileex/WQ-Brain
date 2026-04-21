# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WQ-Brain is a WorldQuant Brain alpha simulator — it submits FASTEXPR formulas to the WorldQuant Brain API, waits for backtest results, and collects performance metrics. The goal is to find alphas that pass WorldQuant's IS (In-Sample) criteria for competition submission.

## Running

1. Copy `credentials.json.example` to `credentials.json` and fill in email/password
2. Configure alpha parameters in `parameters.py` (the `DATA` list)
3. Run `python main.py`

Alpha results go to `data/api_<timestamp>.csv` and logs to `data/api_<timestamp>.log`.

## Commands

- `python main.py` — Run the main simulation loop. Submits alphas from `parameters.py`, collects results, retries failed ones.
- `python commands.py` — Print counts of each alpha generation function (useful for estimating runtime).
- `python scrape_alphas.py` — Scrape the user's existing alphas that passed IS checks, saves to `data/alpha_scrape_result_<timestamp>.csv`.
- `python submit_alphas.py <csv>` — Submit alphas from a scrape result CSV (best ones first by score).

## Architecture

```
main.py                  WQSession (requests.Session subclass)
  ├── login()            HTTP Basic Auth → WQ Brain API
  ├── simulate(data)     POST alpha → poll for results → CSV output
  │     └── ThreadPoolExecutor(max_workers=10)
  └── retry loop         Resubmits failed/unfinished alphas

scrape_alphas.py         Scrape existing alphas via GET /users/self/alphas
  └── scrape(result)     Check IS pass, SELF_CORRELATION, clean alpha code

submit_alphas.py         POST /alphas/{id}/submit for each scraped alpha

commands.py              Alpha formula generator (FASTEXPR grammar)
  ├── from_wq_1/2/3()    Hand-crafted formula templates
  ├── from_arxiv()        101 formulas from the 1601.00991 paper
  ├── scale_and_corr()    Scale/correlation combinations
  └── sample_1/2/3()     Additional formula generators

parameters.py            Configuration: DATA list (universe, region, decay, etc.)
                          and FASTEXPR operator constants (PRICES, TS_OP_1D1P, etc.)

database.py              Minimal SQLAlchemy model for alpha result storage
```

## FASTEXPR Language Reference (from parameters.py)

- **Prices/Volumes**: `open`, `high`, `low`, `close`, `vwap`, `returns`, `volume`, `adv20`, `cap`
- **Unary ops**: `rank`, `sigmoid`, `exp`, `fraction`, `log`, `log_diff`, `scale`, `zscore`
- **Time-series ops (1 param)**: `ts_product`, `ts_std_dev`, `ts_rank`, `ts_sum`, `ts_entropy`, `ts_av_diff`, `ts_arg_max`, `ts_decay_linear`, `ts_delay`, `ts_delta`, `ts_ir`, `ts_max`, `ts_median`, `ts_min`, `ts_skewness`, `ts_kurtosis`
- **Time-series ops (2 params)**: `ts_corr`
- **Group ops**: `group_zscore`, `group_std_dev`, `group_rank`, `group_sum`, `group_scale`, `group_max`, `group_median`
- **Group dimensions**: `market`, `sector`, `industry`, `subindustry`
- **Binary ops**: `+`, `-`, `*`, `/`, `^`
- **Conditionals**: ternary `? :` with `>`, `<`, `=`

## IS Pass Criteria

From README.md:
- `sharpe > 1.25`
- `turnover > 1` and `turnover < 70`
- `subsharpe` (threshold unspecified)
- `fitness >= 1`
- Weight well distributed (CONCENTRATED_WEIGHT check)

## Key Implementation Details

- `WQSession.login()` handles biometric auth — if the API returns an `inquiry` field, it prompts the user to complete biometric auth via browser, then resubmits.
- Auto-retry on network errors (gateway timeouts) with exponential-style retry inside `simulate()`.
- Alpha codes are stripped of comments (lines containing `#`) before submission.
- The `from_arxiv()` function maps old 1601.00991 paper function names to FASTEXPR equivalents (e.g., `SignedPower` → `signed_power`, `Ts_` prefix stripped, `?` ternary syntax preserved).
- Threading: 10 workers, but WorldQuant API enforces ~3 concurrent simulations per account, so parallelism is bounded server-side.
