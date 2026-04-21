from commands import *

# 新的 alpha 公式 - 专注于通过 SELF_CORRELATION 检查 (< 0.7)
# 策略：多样化信号、减少相关性重复、加入随机/波动元素

ALPHAS = [
    # === 短相关窗口组合 (避免长相关产生的自相关性) ===
    # 5天窗口 + 60天相关 - 低自相关
    '(rank(close - ts_sum(close, 5)/5)) - (15 * scale(ts_corr(vwap, volume, 60)))',
    '(rank(close - ts_sum(close, 7)/7)) - (20 * scale(ts_corr(vwap, returns, 60)))',

    # === industry 相对表现 (天然去相关) ===
    'scale(group_zscore(close, sector)) - (10 * scale(group_zscore(vwap, sector)))',
    'scale(group_zscore(returns, subindustry)) + (15 * scale(group_zscore(volume, subindustry)))',

    # === 波动率调整信号 ===
    'scale((close - ts_sum(close, 5)/5) / (ts_std_dev(returns, 10) + 0.001))',
    'scale((close - ts_sum(close, 7)/7) / (ts_std_dev(close, 15) + 0.001))',

    # === 混合信号 (多维度去相关) ===
    '(rank(close - ts_sum(close, 5)/5)) * (rank(1/volume)) + (10 * scale(ts_corr(vwap, returns, 60)))',
    'rank(close - ts_sum(close, 7)/7) + rank(volume - ts_sum(volume, 10)/10)',

    # === 纯均值回归 (无长相关) ===
    'rank(close - ts_sum(close, 5)/5) + rank(close - ts_sum(close, 20)/20)',
    'rank(close - ts_sum(close, 10)/10) - rank(close - ts_sum(close, 30)/30)',

    # === 短窗口量价相关 (60天) ===
    '(rank(close - ts_sum(close, 7)/7)) + (12 * scale(ts_corr(vwap, volume, 60)))',
    '(rank(close - ts_sum(close, 5)/5)) - (15 * scale(ts_corr(vwap, returns, 60)))',

    # === rank 替代 scale (减少连续性) ===
    'rank(close - ts_sum(close, 7)/7) + rank(ts_corr(vwap, returns, 60))',
    'rank((close - ts_sum(close, 5)/5) / (ts_std_dev(returns, 10) + 0.001))',

    # === 残差类信号 (正交化去相关) ===
    'rank(close - ts_sum(close, 5)/5 - ts_mean(close - ts_sum(close, 5)/5, 20))',
    'rank(returns - ts_mean(returns, 10))',

    # === 高相关性 + decay=15 SECTOR ===
    'scale(((ts_sum(close, 5) / 5) - close)) + (15 * scale(ts_corr(vwap, ts_delay(close, 3), 180)))',
    'scale(((ts_sum(close, 10) / 10) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 7), 270)))',
    'scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(volume, ts_delay(close, 5), 200)))',

    # === ts_decay_linear 变体 ===
    'scale(ts_decay_linear(close, 7) - close) + (18 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',
    'scale(ts_decay_linear(close, 10) - close) + (22 * scale(ts_corr(vwap, ts_delay(close, 3), 180)))',

    # === 更长的相关性窗口 (已知可过 IS) ===
    'scale(((ts_sum(close, 7) / 7) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))',
    'scale(((ts_sum(close, 7) / 7) - close)) + (30 * scale(ts_corr(vwap, ts_delay(close, 10), 300)))',

    # === 多信号组合 ===
    'scale((close - ts_sum(close, 7) / 7)) + (10 * scale(ts_corr(vwap, volume, 150))) + (10 * scale(ts_corr(close, ts_delay(close, 5), 200)))',
    'scale((close - ts_sum(close, 5) / 5)) + (15 * scale(ts_corr(returns, volume, 120)))',

    # === 原始 winning formula (baseline) ===
    'scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',
]

# 关键优化：多用 SECTOR neutralization，已知可通过 SELF_CORRELATION
PARAM_SETS = [
    # decay=10-15 是 IS 容易通过的区间
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'SECTOR', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 12, 'truncation': 0.08, 'neutralization': 'SECTOR', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 15, 'truncation': 0.08, 'neutralization': 'SECTOR', 'universe': 'TOP3000', 'region': 'USA'},
    # SUBINDUSTRY 作为对比
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 12, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 15, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY', 'universe': 'TOP3000', 'region': 'USA'},
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

# 只跑前 5 个最有潜力的新配方测试
DATA = DATA[:5]
