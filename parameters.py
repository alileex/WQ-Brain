from commands import *

# 新公式设计策略：降低 SELF_CORRELATION
# 核心思路：
# 1. rank() 变换打破时间自相关
# 2. 多因子组合：均值回归 + 动量 + 成交量 混合
# 3. 条件信号：不同市场状态用不同策略
# 4. 行业相对信号：截面比较降低市场整体自相关
# 5. 波动率/成交量信号：与价格信号解耦
# 6. 长窗口信号：用更长时间窗口平滑

ALPHAS = [
    # =============================================================
    # 家族1: 动量信号 (与均值回归解耦)
    # =============================================================
    # 简单动量反转 - rank 变换降低自相关
    'rank(-ts_delta(close, 1))',
    'rank(-ts_delta(close, 2))',
    'rank(-ts_delta(close, 5))',
    # rank(returns) 形态
    'rank(-returns)',
    'rank(-ts_mean(returns, 5))',
    # 动量 + 成交量混合
    'rank(-ts_delta(close, 1)) * rank(-volume / ts_mean(volume, 20))',

    # =============================================================
    # 家族2: 成交量异常信号 (与价格信号解耦)
    # =============================================================
    # 成交量 rank 信号
    'rank(volume / ts_mean(volume, 20))',
    'rank(-ts_std_dev(volume / ts_mean(volume, 20), 5))',
    # 成交量 - 价格 组合
    'rank(volume / ts_mean(volume, 20)) + rank(-ts_delta(close, 1))',

    # =============================================================
    # 家族3: 条件信号 (打破单向偏见)
    # =============================================================
    # 波动率条件：如果短期波动高则用不同策略
    'ts_std_dev(returns, 5) > ts_mean(ts_std_dev(returns, 20), 5) ? rank(-ts_delta(close, 1)) : rank(-ts_delta(close, 5))',
    # 趋势条件：趋势向上用动量，向下用反转
    'ts_delta(close, 5) > 0 ? rank(-ts_delta(close, 1)) : rank(ts_delta(close, 1))',

    # =============================================================
    # 家族4: 行业相对信号 (截面比较)
    # =============================================================
    # 行业中相对强弱
    'group_zscore(ts_delta(close, 1), sector)',
    'group_zscore(-returns, sector)',
    # 行业中相对成交量异常
    'group_zscore(volume / ts_mean(volume, 20), sector)',

    # =============================================================
    # 家族5: 波动率信号 (与价格动量解耦)
    # =============================================================
    # 短期 vs 长期波动率差异
    'rank(ts_std_dev(returns, 5) - ts_std_dev(returns, 20))',
    'rank(-ts_std_dev(returns, 5))',
    # 收益率离散度
    'rank(-ts_std_dev(returns, 10))',

    # =============================================================
    # 家族6: 改进版均值回归 + ts_corr (加入 rank 变换)
    # =============================================================
    # rank 变换后的均值回归 + 相关性
    'rank(scale(((ts_sum(close, 7) / 7) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360))))',
    # 更短窗口的均值回归
    'rank(scale(((ts_sum(close, 3) / 3) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 3), 200))))',
    # 长窗口均值回归
    'rank(scale(((ts_sum(close, 15) / 15) - close)) + (25 * scale(ts_corr(vwap, ts_delay(close, 7), 400))))',
    # 无 scale 系数的 rank 版本
    'scale(rank(((ts_sum(close, 7) / 7) - close))) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))',

    # =============================================================
    # 家族7: 多因子组合 (分散信号来源)
    # =============================================================
    # 均值回归 + 成交量异常
    'rank(scale(((ts_sum(close, 7) / 7) - close))) + (3 * rank(volume / ts_mean(volume, 20)))',
    # 动量 + 波动率
    'rank(-ts_delta(close, 5)) + rank(-ts_std_dev(returns, 10))',
    # 均值回归 + 动量
    'scale(((ts_sum(close, 7) / 7) - close)) + (0.5 * rank(-ts_delta(close, 5))) + (25 * scale(ts_corr(vwap, ts_delay(close, 5), 360)))',

    # =============================================================
    # 家族8: ts_decay_linear 变体
    # =============================================================
    'rank(scale(ts_decay_linear(close, 7) - close) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230))))',
    'rank(-ts_decay_linear(ts_delta(close, 1), 5))',
    'scale(ts_decay_linear(close - ts_mean(close, 10), 7))',

    # =============================================================
    # 家族9: 杠杆/乘数效应
    # =============================================================
    'signed_power(close / ts_delay(close, 1) - 1, 2)',
    'signed_power(returns, 2)',
    'signed_power(ts_delta(close, 1) / ts_delay(close, 1), 3)',

    # =============================================================
    # 家族10: 高Sharpe的已知公式变体
    # =============================================================
    # E5rm67ZK 类似公式 - 简单反转 + 波动率
    '(-1 * ts_delta(close, 1)) + (0.5 * rank(-ts_std_dev(returns, 10)))',
    # arxiv 精选公式变体
    '(-1 * ts_corr(rank(ts_delta(log(volume), 2)), rank(returns), 6))',
    'rank(((open - (ts_sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap))))',
    '(-1 * ts_sum(rank(ts_corr(rank(high), rank(volume), 3)), 3))',
    'scale(((ts_sum(close, 7) / 7) - close)) + (20 * scale(ts_corr(vwap, ts_delay(close, 5), 230)))',

    # =============================================================
    # 家族11: ts_corr 关联信号 (不同资产间相关性)
    # =============================================================
    # 价格-成交量相关性
    'rank(ts_corr(ts_delta(close, 1), ts_delta(volume, 1), 10))',
    'rank(-ts_corr(ts_delta(close, 1), ts_delta(volume, 1), 20))',
    # 价格-成交量 lag 相关性
    'rank(-ts_corr(close, volume, 10))',
    'rank(-ts_corr(open, volume, 10))',
    'rank(ts_corr(close, ts_delay(volume, 1), 5))',
    # 高-低波动率相关性
    'rank(-ts_corr(high - low, volume, 10))',
    # 跨资产相关性
    'rank(-ts_corr(vwap, ts_mean(volume, 20), 5))',

    # =============================================================
    # 家族12: ts_rank 时间序列排名信号
    # =============================================================
    'rank(ts_rank(-ts_delta(close, 1), 10))',
    'rank(ts_rank(-ts_delta(close, 1), 20))',
    'rank(ts_rank(-returns, 5))',
    'rank(ts_rank(ts_delta(close, 5), 10))',
    # ts_rank + 成交量
    'rank(ts_rank(volume / ts_mean(volume, 20), 10))',
    # ts_rank + 波动率
    'rank(ts_rank(-ts_std_dev(returns, 10), 20))',

    # =============================================================
    # 家族13: 多时间框架混合
    # =============================================================
    # 短期 vs 长期信号差
    'rank(-ts_delta(close, 1)) - rank(-ts_delta(close, 10))',
    'rank(-ts_delta(close, 2)) - rank(-ts_delta(close, 20))',
    # 不同频率动量
    'rank(-ts_mean(returns, 3)) + rank(-ts_mean(returns, 20))',
    # 多周期成交量信号
    'rank(volume / ts_mean(volume, 5)) - rank(volume / ts_mean(volume, 20))',

    # =============================================================
    # 家族14: 市场微观结构
    # =============================================================
    # 日内价差代理
    'rank((close - open) / (high - low + 0.001))',
    'rank((vwap - close) / (high - low + 0.001))',
    # 相对开盘价变化
    'rank(close / open - 1)',
    'rank((close - ts_delay(open, 1)) / ts_delay(open, 1))',
    # 收盘-开盘比率
    '(close - open) / ts_mean(close - open, 20)',
    # 实体大小 (蜡烛线实体)
    'rank(abs(close - open) / (high - low + 0.001))',

    # =============================================================
    # 家族15: ts_sum 累积信号 (动量累积)
    # =============================================================
    'rank(ts_sum(-ts_delta(close, 1), 5))',
    'rank(ts_sum(-ts_delta(close, 1), 10))',
    'rank(ts_sum(returns, 5))',
    'rank(ts_sum(returns, 10))',
    # 累积量信号
    'rank(ts_sum(volume / ts_mean(volume, 20) - 1, 5))',

    # =============================================================
    # 家族16: group 操作扩展
    # =============================================================
    # group_rank 行业排名
    'group_rank(-ts_delta(close, 1), sector)',
    'group_rank(-ts_delta(close, 1), subindustry)',
    # group_max/median 行业极端值
    'group_max(ts_delta(close, 1), sector) - ts_delta(close, 1)',
    'ts_delta(close, 1) - group_median(ts_delta(close, 1), sector)',
    # group_sum 行业总和异常
    'rank(ts_delta(close, 1) / group_sum(ts_delta(close, 1), sector))',

    # =============================================================
    # 家族17: 条件+中性化组合
    # =============================================================
    # 行业中性 + 条件
    'group_zscore(ts_delta(close, 1) > ts_mean(ts_delta(close, 5), 20) ? ts_delta(close, 1) : -ts_delta(close, 1), sector)',
    # 波动率条件 + 行业中性
    'group_zscore(ts_std_dev(returns, 5) > ts_std_dev(returns, 20) ? -ts_delta(close, 1) : ts_delta(close, 1), sector)',
    # 多条件组合
    'ts_std_dev(returns, 5) > ts_mean(ts_std_dev(returns, 20), 10) ? group_zscore(-ts_delta(close, 1), sector) : group_zscore(ts_delta(close, 1), sector)',

    # =============================================================
    # 家族18: ts_delta 变化率信号
    # =============================================================
    # 变化率信号
    'rank(ts_delta(close / ts_delay(close, 5) - 1, 1))',
    'rank(ts_delta(close / ts_delay(close, 10) - 1, 1))',
    # 二阶变化率
    'rank(ts_delta(ts_delta(close, 1), 1))',
    # 累积变化率
    'rank(ts_delta(close, 1) / ts_delay(close, 1))',

    # =============================================================
    # 家族19: 波动率调整信号
    # =============================================================
    # 波动率调整后的动量
    'rank(-ts_delta(close, 1) / ts_std_dev(returns, 10))',
    'rank(-ts_delta(close, 1) / ts_std_dev(returns, 20))',
    # 相对波动率信号
    'rank(-ts_delta(close, 1) * (ts_std_dev(returns, 20) / (ts_std_dev(returns, 5) + 0.001)))',
    # 波动率倒数
    'rank(1 / ts_std_dev(returns, 10))',

    # =============================================================
    # 家族20: 混合 rank 变换
    # =============================================================
    # 双 rank 变换
    'rank(rank(-ts_delta(close, 1)))',
    # rank + scale
    'scale(rank(-ts_delta(close, 1)))',
    # zscore + rank
    'rank(zscore(-ts_delta(close, 5)))',
    # rank 减均值
    'rank(-ts_delta(close, 1)) - rank(ts_mean(-ts_delta(close, 1), 20))',

    # =============================================================
    # 家族21: ts_arg_max/min 极值检测
    # =============================================================
    # 最近 N 天最高点距离
    'rank(ts_arg_max(close, 10) - ts_len(close))',
    'rank(-(ts_arg_max(close, 20) - ts_len(close)))',
    # 最低点距离
    'rank(ts_arg_min(close, 10) - ts_len(close))',
    # 结合成交量
    'rank(ts_arg_max(volume, 5) - ts_len(volume))',

    # =============================================================
    # 家族22: 成交量-价格背离
    # =============================================================
    # 价格上涨但成交量低 (可能反转)
    'rank(-ts_delta(close, 5)) * rank(volume / ts_mean(volume, 20))',
    # 价格下跌但成交量高
    'rank(ts_delta(close, 5)) * rank(volume / ts_mean(volume, 20))',
    # 背离信号
    'rank((ts_delta(close, 5) > 0 ? -1 : 1) * ts_corr(volume, close, 10))',

    # =============================================================
    # 家族23: 均值回归 + 随机指标 (RSI 类)
    # =============================================================
    # RSI 类公式
    'rank(-(ts_sum(ts_max(close - ts_delay(close, 1), 0), 14) / ts_sum(ts_max(ts_delay(close, 1) - close, 0), 14)))',
    # 简化版 RSI
    'rank(-ts_delta(close, 1) / ts_sum(ts_abs(ts_delta(close, 1)), 10))',

    # =============================================================
    # 家族24: 对数变换信号
    # =============================================================
    # log 变换降低极端值影响
    'rank(-ts_delta(log(close), 1))',
    'rank(-ts_delta(log(volume), 2))',
    'rank(ts_corr(log(volume), log(close), 10))',
    # log 变换 + scale
    'rank(scale(-ts_delta(log(close), 1)))',

    # =============================================================
    # 家族25: 截面排序 (横跨股票)
    # =============================================================
    # 今日相对强弱 (截面 rank)
    'rank(-ts_delta(close, 1))',
    # 多日累积截面排名
    'rank(ts_sum(-ts_delta(close, 1), 5))',
    # 截面波动率排名
    'rank(-ts_std_dev(returns, 10))',
]

# 参数组合：针对不同公式优化
PARAM_SETS = [
    # decay=0：无延迟，高换手率
    {'decay': 0,  'truncation': 0.08, 'neutralization': 'MARKET',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 0,  'truncation': 0.08, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    # decay=5：短延迟
    {'decay': 5,  'truncation': 0.08, 'neutralization': 'MARKET',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 5,  'truncation': 0.08, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 5,  'truncation': 0.08, 'neutralization': 'SUBINDUSTRY','universe': 'TOP3000', 'region': 'USA'},
    # decay=10：中延迟
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'MARKET',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY','universe': 'TOP3000', 'region': 'USA'},
    # decay=15：长延迟
    {'decay': 15, 'truncation': 0.08, 'neutralization': 'MARKET',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 15, 'truncation': 0.08, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    # decay=15 with SUBINDUSTRY
    {'decay': 15, 'truncation': 0.08, 'neutralization': 'SUBINDUSTRY','universe': 'TOP3000', 'region': 'USA'},
    # 低 truncation：高换手率
    {'decay': 5,  'truncation': 0.05, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    {'decay': 10, 'truncation': 0.05, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    # 高 truncation：低换手率
    {'decay': 5,  'truncation': 0.12, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'USA'},
    # 不同 universe
    {'decay': 5,  'truncation': 0.08, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'CHN'},
    {'decay': 10, 'truncation': 0.08, 'neutralization': 'SECTOR',     'universe': 'TOP3000', 'region': 'CHN'},
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
