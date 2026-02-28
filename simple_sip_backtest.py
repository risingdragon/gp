import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import platform

system_name = platform.system()
if system_name == 'Windows':
    font_names = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong', 'KaiTi']
    found = False
    for font_name in font_names:
        try:
            font_prop = font_manager.FontProperties(family=font_name)
            plt.rcParams['font.sans-serif'] = [font_name]
            plt.rcParams['axes.unicode_minus'] = False
            found = True
            break
        except:
            continue

print("=" * 80)
print("青农商行(002958) 定投策略回测")
print("=" * 80)

df = pd.read_csv('qrcb_historical_data.csv')
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

print(f"\n数据时间范围: {df.index[0]} 至 {df.index[-1]}")
print(f"总交易日数: {len(df)}")
print(f"首日收盘价: {df['close'].iloc[0]:.2f}")
print(f"末日收盘价: {df['close'].iloc[-1]:.2f}")

monthly_investment = 1000

def backtest_sip(data, invest_day=1):
    data = data.copy()
    data['year_month'] = data.index.to_period('M')
    
    total_invested = 0
    total_shares = 0
    investment_dates = []
    
    for year_month in data['year_month'].unique():
        month_data = data[data['year_month'] == year_month]
        
        if invest_day == 'lowest':
            invest_idx = month_data['low'].idxmin()
        elif invest_day == 'highest':
            invest_idx = month_data['high'].idxmax()
        else:
            if invest_day == -1:
                invest_idx = month_data.index[-1]
            else:
                invest_idx = min(invest_day - 1, len(month_data) - 1)
                if invest_idx < 0:
                    continue
                invest_idx = month_data.index[invest_idx]
        
        if invest_idx not in month_data.index:
            continue
            
        invest_price = month_data.loc[invest_idx, 'close']
        
        shares = monthly_investment / invest_price
        
        total_invested += monthly_investment
        total_shares += shares
        
        investment_dates.append({
            'date': invest_idx,
            'price': invest_price,
            'shares': shares
        })
    
    final_value = total_shares * data['close'].iloc[-1]
    total_profit = final_value - total_invested
    profit_rate = (total_profit / total_invested) * 100 if total_invested > 0 else 0
    
    years = (data.index[-1] - data.index[0]).days / 365.25
    annualized_return = ((final_value / total_invested) ** (1 / years) - 1) * 100 if years > 0 and total_invested > 0 else 0
    
    return {
        'total_invested': total_invested,
        'final_value': final_value,
        'total_profit': total_profit,
        'profit_rate': profit_rate,
        'annualized_return': annualized_return,
        'investment_count': len(investment_dates),
        'investment_dates': investment_dates
    }

strategies = [
    ("每月1日定投", 1),
    ("每月15日定投", 15),
    ("每月最后1日定投", -1),
    ("每月最低点定投(理想)", 'lowest'),
    ("每月最高点定投(最差)", 'highest'),
]

results = {}
for name, day in strategies:
    results[name] = backtest_sip(df, day)

print("\n" + "=" * 80)
print("策略对比结果")
print("=" * 80)
print(f"{'策略名称':<25} {'定投次数':<10} {'总投入(元)':<12} {'期末资产(元)':<15} {'总收益(元)':<12} {'收益率(%)':<12} {'年化(%)':<10}")
print("-" * 100)

valid_results = {k: v for k, v in results.items() if v['investment_count'] > 0}
sorted_strategies = sorted(valid_results.items(), key=lambda x: x[1]['profit_rate'], reverse=True)

for name, result in sorted_strategies:
    print(f"{name:<25} "
          f"{result['investment_count']:<10} "
          f"{result['total_invested']:<12.2f} "
          f"{result['final_value']:<15.2f} "
          f"{result['total_profit']:<12.2f} "
          f"{result['profit_rate']:<12.2f} "
          f"{result['annualized_return']:<10.2f}")

print("\n" + "=" * 80)
if sorted_strategies:
    best_strategy = sorted_strategies[0]
    worst_strategy = sorted_strategies[-1]
    print(f"最优策略: {best_strategy[0]} (收益率: {best_strategy[1]['profit_rate']:.2f}%)")
    print(f"最差策略: {worst_strategy[0]} (收益率: {worst_strategy[1]['profit_rate']:.2f}%)")
    print(f"策略差异: {best_strategy[1]['profit_rate'] - worst_strategy[1]['profit_rate']:.2f}%")

    one_time_shares = best_strategy[1]['total_invested'] / df['close'].iloc[0]
    one_time_value = one_time_shares * df['close'].iloc[-1]
    one_time_profit = one_time_value - best_strategy[1]['total_invested']
    one_time_profit_rate = (one_time_profit / best_strategy[1]['total_invested']) * 100

    print(f"\n一次性买入对比: {one_time_profit:.2f} 元 ({one_time_profit_rate:.2f}%)")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

strategy_names = list(valid_results.keys())
profit_rates = [valid_results[name]['profit_rate'] for name in strategy_names]
colors = ['green' if x >= 0 else 'red' for x in profit_rates]

bars = axes[0, 0].barh(strategy_names, profit_rates, color=colors, alpha=0.7)
axes[0, 0].set_xlabel('收益率 (%)', fontsize=12)
axes[0, 0].set_title('各策略收益率对比', fontsize=14, fontweight='bold')
axes[0, 0].axvline(x=0, color='black', linestyle='-', linewidth=0.8)
axes[0, 0].grid(True, alpha=0.3, axis='x')

for i, bar in enumerate(bars):
    width = bar.get_width()
    axes[0, 0].text(width + (0.5 if width >= 0 else -3), 
                   bar.get_y() + bar.get_height()/2,
                   f'{profit_rates[i]:.2f}%',
                   va='center', fontsize=10)

annualized_returns = [valid_results[name]['annualized_return'] for name in strategy_names]
colors = ['green' if x >= 0 else 'red' for x in annualized_returns]

bars2 = axes[0, 1].barh(strategy_names, annualized_returns, color=colors, alpha=0.7)
axes[0, 1].set_xlabel('年化收益率 (%)', fontsize=12)
axes[0, 1].set_title('各策略年化收益率对比', fontsize=14, fontweight='bold')
axes[0, 1].axvline(x=0, color='black', linestyle='-', linewidth=0.8)
axes[0, 1].grid(True, alpha=0.3, axis='x')

for i, bar in enumerate(bars2):
    width = bar.get_width()
    axes[0, 1].text(width + (0.1 if width >= 0 else -0.5), 
                    bar.get_y() + bar.get_height()/2,
                    f'{annualized_returns[i]:.2f}%',
                    va='center', fontsize=10)

axes[1, 0].plot(df.index, df['close'], label='收盘价', linewidth=1.5, color='blue')
axes[1, 0].set_title('青农商行(002958) 价格走势', fontsize=14, fontweight='bold')
axes[1, 0].set_ylabel('价格 (元)', fontsize=12)
axes[1, 0].legend(fontsize=10)
axes[1, 0].grid(True, alpha=0.3)

for name, result in valid_results.items():
    if len(result['investment_dates']) > 0:
        dates = [x['date'] for x in result['investment_dates']]
        prices = [x['price'] for x in result['investment_dates']]
        if name == "每月最低点定投(理想)":
            axes[1, 0].scatter(dates, prices, color='green', s=30, alpha=0.6, label=name)
        elif name == "每月最高点定投(最差)":
            axes[1, 0].scatter(dates, prices, color='red', s=30, alpha=0.6, label=name)

axes[1, 0].legend(fontsize=9, loc='best')

if valid_results:
    total_invested_ref = valid_results['每月1日定投']['total_invested'] if '每月1日定投' in valid_results else list(valid_results.values())[0]['total_invested']
    for name, result in valid_results.items():
        portfolio_values = []
        current_shares = 0
        invest_dict = {x['date']: x['shares'] for x in result['investment_dates']}
        
        for date in df.index:
            if date in invest_dict:
                current_shares += invest_dict[date]
            value = current_shares * df.loc[date, 'close']
            portfolio_values.append(value)
        
        if name == "每月最低点定投(理想)":
            axes[1, 1].plot(df.index, portfolio_values, label=name, linewidth=2, color='green')
        elif name == "每月最高点定投(最差)":
            axes[1, 1].plot(df.index, portfolio_values, label=name, linewidth=2, color='red')
        else:
            axes[1, 1].plot(df.index, portfolio_values, label=name, linewidth=1.5, alpha=0.7)

    axes[1, 1].axhline(y=total_invested_ref, color='orange', linestyle='--', linewidth=2, label='累计投入')
    axes[1, 1].set_title('各策略资产净值走势对比', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('日期', fontsize=12)
    axes[1, 1].set_ylabel('资产市值 (元)', fontsize=12)
    axes[1, 1].legend(fontsize=9, loc='best')
    axes[1, 1].grid(True, alpha=0.3)

annot = None

def format_coord(x, y):
    try:
        from matplotlib.dates import num2date
        current_date = num2date(x)
        target_date = pd.Timestamp(current_date)
        nearest_date = df.index.asof(target_date)
        
        if nearest_date is not pd.NaT:
            current_price = df.loc[nearest_date, 'close']
            date_str = nearest_date.strftime('%Y-%m-%d')
            return f'date={date_str}, 收盘价={current_price:.2f}元, y={y:.2f}'
    except:
        pass
    return f'x={x:.4f}, y={y:.4f}'

axes[1, 0].format_coord = format_coord
axes[1, 1].format_coord = format_coord

plt.tight_layout()
plt.savefig('sip_comparison.png', dpi=300, bbox_inches='tight')
print("\n多策略对比图表已保存为: sip_comparison.png")
print("\n提示: 在价格走势或资产净值图表上，鼠标悬停在坐标区域即可查看对应日期的收盘价")
plt.show()

print("\n" + "=" * 80)
print("回测分析完成！")
print("=" * 80)
