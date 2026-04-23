# Repository Guidelines

## Project Structure & Module Organization
This repository is a small Python automation tool for WorldQuant Brain alpha simulation and submission. The main entrypoints live at the repo root:

- `main.py` handles authentication, simulation requests, polling, and CSV/log output.
- `commands.py` contains formula generators.
- `parameters.py` defines the active `ALPHAS`, parameter sets, and the `DATA` payload consumed by `main.py`.
- `scrape_alphas.py` exports passed alphas to `data/`.
- `submit_alphas.py` submits the best scraped results.
- `data/` stores generated CSV and log files such as `data/api_<timestamp>.csv`.

## Build, Test, and Development Commands
There is no formal build step. Use a local virtual environment and run scripts directly:

- `python -m venv .venv && source .venv/bin/activate`
- `pip install requests pandas`
- `cp credentials.json.example credentials.json` and fill in account details
- `python main.py` runs the simulation batch from `parameters.py`
- `python commands.py` prints formula-generator counts
- `python scrape_alphas.py` exports passing alphas to `data/`
- `python submit_alphas.py data/alpha_scrape_result_<timestamp>.csv` submits scraped results
- `python -m py_compile *.py` performs a lightweight syntax check before opening a PR

## Coding Style & Naming Conventions
Follow the existing style: 4-space indentation, top-level scripts, and simple module boundaries. Use `snake_case` for functions and variables, `UPPER_CASE` for constants like `ALPHAS` and `PARAM_SETS`, and keep FASTEXPR strings readable in single quotes. Prefer small, direct edits over new abstractions or dependencies.

## Testing Guidelines
There is no committed test suite yet. For changes, run `python -m py_compile *.py` and execute the affected script with a small parameter set in `parameters.py`. When changing CSV output or submission logic, confirm new files appear under `data/` and review the generated `.log` file for retries, throttling, or auth failures.

## Commit & Pull Request Guidelines
Recent history uses short, imperative subjects such as `Fix biometric auth bug` and `Update post-competition scraper`. Keep commits focused on one behavior change and use the subject line to describe intent. PRs should include: a short summary, affected scripts, the commands you ran, and sanitized sample output when the change affects API flows or generated CSV/log files.

## Security & Configuration Tips
Never commit `credentials.json` or raw account data. Use `credentials.json.example` as the template, keep generated artifacts in `data/`, and redact alpha links, credentials, and logs before sharing externally.
