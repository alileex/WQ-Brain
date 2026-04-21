from commands import *

# 基于 winning formula 的变体 + 新模式
ALPHAS = [
    # Winning formula 的变体（改窗口期）
    'scale(((ts_sum(close, 5) / 5) - close)) + (15 * scale(ts_corr(vwap, ts_delay(close, 3), 180)))',
    'scale(((ts_sum(close, 10) / 10) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 7), 270)))',
    'scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(volume, ts_delay(close, 5), 200)))',

    # 用 ts_decay_linear 替代 ts_sum
    'scale(ts_decay_linear(close, 7) - close) + (18 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',
    'scale(ts_decay_linear(close, 10) - close) + (22 * scale(ts_corr(vwap, ts_delay(close, 3), 180)))',

    # 多信号组合
    'scale((close - ts_sum(close, 7) / 7)) + (10 * scale(ts_corr(vwap, volume, 150))) + (10 * scale(ts_corr(close, ts_delay(close, 5), 200)))',
    'scale((close - ts_sum(close, 5) / 5)) + (15 * scale(ts_corr(returns, volume, 120)))',

    # rank 替代 scale
    'rank((close - ts_sum(close, 7) / 7)) + (20 * rank(ts_corr(vwap, ts_delay(close, 5), 230)))',
    'rank((close - ts_sum(close, 10) / 10)) + (15 * rank(ts_corr(vwap, ts_delay(close, 3), 180)))',

    # group_zscore 中性化
    'scale(group_zscore((close - ts_sum(close, 7) / 7), subindustry)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',
    'scale(group_zscore((close - ts_sum(close, 5) / 5), sector)) + (15 * scale(ts_corr(vwap, ts_delay(close, 3), 180)))',

    # ts_std_dev 波动率调整
    'scale(((close - ts_sum(close, 7) / 7) / (ts_std_dev(returns, 20) + 0.01))) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',

    # 更长的相关性窗口
    'scale(((ts_sum(close, 7) / 7) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))',
    'scale(((ts_sum(close, 7) / 7) - close)) + (30 * scale(ts_corr(vwap, ts_delay(close, 10), 300)))',

    # 原始 winning formula（再跑一次确认）
    'scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',
]

PARAM_SETS = [
    # decay=10 是最优区间
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 12, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 15, 'truncation': 0.08, 'neutralization': 'SECTOR', 'universe': 'TOP3000', 'region': 'USA'},
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
