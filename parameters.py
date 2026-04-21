from commands import *

ALPHAS = [
    # Simple direct formulas - high information density
    '(-1 * ts_delta(returns, 1))',
    '(-1 * ts_delta(close, 1))',
    '(close - ts_delay(close, 1))',
    'rank(ts_delta(returns, 1))',
    'rank(-ts_delta(close, 1))',
    # Mean reversion - short term
    '(-1 * (close - ts_delay(close, 1)))',
    '(-1 * (close - ts_sum(close, 2) / 2))',
    '(-1 * (close - ts_sum(close, 3) / 3))',
    # Volume-based short term
    'ts_delta(volume, 1)',
    '(-1 * ts_delta(volume, 1))',
    'rank(ts_delta(volume, 1))',
    # Rank-based signals
    'rank(close - ts_min(close, 5))',
    'rank(ts_max(close, 5) - close)',
    'rank((close - vwap) / (high - low + 0.001))',
    # Correlation short term
    '(-1 * ts_corr(ts_delta(close, 1), ts_delta(volume, 1), 3))',
    # Returns-based
    '(-1 * rank(returns))',
    '(-1 * rank(ts_delta(returns, 2)))',
    # VWAP deviation
    '(vwap - close) / (high - low + 0.001)',
    'rank((vwap - close) / (high - low + 0.001))',
    # ts_arg_max/min signals
    '(-1 * ts_arg_max(returns, 3))',
    'ts_min(returns, 3)',
    # Scale-based combinations
    'scale(ts_delta(close, 1))',
    'scale(-ts_delta(volume, 1))',
    '(-1 * scale(ts_delta(returns, 2)))',
    # ts_decay_linear with very short windows
    '(-1 * ts_decay_linear(ts_delta(close, 1), 3))',
    'ts_decay_linear(-ts_delta(volume, 1), 3)',
    # ts_rank combinations
    '(-1 * ts_rank(ts_delta(close, 1), 5))',
    'ts_rank(-ts_delta(volume, 1), 5)',
    # ts_std_dev based
    '(-1 * ts_std_dev(returns, 5))',
    'ts_std_dev(returns, 5)',
    # ts_sum short window
    'ts_sum(returns, 2)',
    '(-1 * ts_sum(returns, 3))',
    # ts_product
    '(-1 * ts_product(returns, 3))',
    # ts_corr with short windows
    '(-1 * ts_corr(returns, volume, 5))',
    'ts_corr(returns, volume, 5)',
    # Signed power
    'signed_power(returns, 2)',
    '(-1 * signed_power(returns, 2))',
    # Log_diff
    '(-1 * log_diff(close))',
    'log_diff(close)',
    # Group operations - short term
    '(-1 * group_zscore(ts_delta(close, 1), subindustry))',
    'group_zscore(ts_delta(returns, 2), sector)',
    # Combined signals
    '(-1 * ts_delta(close, 1) * ts_delta(volume, 1))',
    '(-1 * ts_delta(returns, 1) * rank(volume))',
    # ts_av_diff
    '(-1 * ts_av_diff(close, 5))',
    # ts_entropy
    '(-1 * ts_entropy(returns, 10))',
    # ts_skewness/kurtosis
    '(-1 * ts_skewness(returns, 10))',
    'ts_kurtosis(returns, 10)',
]

PARAM_SETS = [
    {'decay': 1, 'truncation': 0.01, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 2, 'truncation': 0.01, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 3, 'truncation': 0.01, 'neutralization': 'SECTOR', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 1, 'truncation': 0.02, 'neutralization': 'SECTOR', 'universe': 'TOP3000', 'region': 'USA'},
]

DATA = [
    {
        'neutralization': params['neutralization'],
        'decay': params['decay'],
        'truncation': params['truncation'],
        'delay': 1,
        'universe': params['universe'],
        'region': params['region'],
        'code': alpha,
    }
    for alpha in ALPHAS
    for params in PARAM_SETS
]
