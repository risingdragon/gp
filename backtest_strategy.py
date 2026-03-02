import pandas as pd
import numpy as np
import matplotlib.dates as mdates
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

print("=" * 60)
print("青农商行(002958)定投策略回测")
print("=" * 60)

df = pd.read_csv('qrcb_historical_data.csv')
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

print(f"\n数据时间范围: {df.index[0]} 至 {df.index[-1]}")
print(f"总交易日数: {len(df)}")
print(f"首日收盘价: {df['close'].iloc[0]:.2f}")
print(f"末日收盘价: {df['close'].iloc[-1]:.2f}")

# 输入开始日期（暂时注释掉，直接使用默认）
# start_date_input = input("\n请输入开始日期 (格式: YYYY-MM-DD, 按Enter使用默认开始日期): ")
# if start_date_input:
#     start_date = pd.to_datetime(start_date_input)
#     # 过滤数据，只保留开始日期之后的数据
#     df = df[df.index >= start_date]
#     print(f"\n回测时间范围: {df.index[0]} 至 {df.index[-1]}")
#     print(f"回测交易日数: {len(df)}")
# else:
print(f"\n使用默认时间范围: {df.index[0]} 至 {df.index[-1]}")

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

invest_day = 11

def backtest_sip_with_open(data, invest_day=11):
    data = data.copy()
    data['year_month'] = data.index.to_period('M')
    
    total_invested = 0
    total_shares = 0
    investment_dates = []
    
    for year_month in data['year_month'].unique():
        month_data = data[data['year_month'] == year_month]
        
        # 寻找11日或之后的第一个交易日
        target_day = invest_day
        invest_date = None
        invest_price = None
        
        # 先找11日当天
        for date in month_data.index:
            if date.day == target_day:
                invest_date = date
                invest_price = month_data.loc[date, 'open']
                break
        
        # 如果11日没开盘，找下一个交易日
        if invest_date is None:
            for date in month_data.index:
                if date.day > target_day:
                    invest_date = date
                    invest_price = month_data.loc[date, 'open']
                    break
        
        # 如果11日之后也没有（月末），就找该月最后一个交易日
        if invest_date is None and len(month_data) > 0:
            invest_date = month_data.index[-1]
            invest_price = month_data.loc[invest_date, 'open']
        
        if invest_date is not None and invest_price is not None:
            shares = monthly_investment / invest_price
            
            total_invested += monthly_investment
            total_shares += shares
            
            investment_dates.append({
                'date': invest_date,
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

result = backtest_sip_with_open(df, invest_day=invest_day)

print(f"\n{'=' * 60}")
print(f"策略: 每月{invest_day}日(或下一个交易日)用开盘价定投 {monthly_investment} 元")
print(f"{'=' * 60}")
print(f"\n定投次数: {result['investment_count']} 次")
print(f"总投入金额: {result['total_invested']:.2f} 元")
print(f"期末总资产: {result['final_value']:.2f} 元")
print(f"总收益: {result['total_profit']:.2f} 元")
print(f"收益率: {result['profit_rate']:.2f}%")
print(f"年化收益率: {result['annualized_return']:.2f}%")

print(f"\n单笔投资对比 (一次性买入 {result['total_invested']:.2f} 元):")
one_time_shares = result['total_invested'] / df['close'].iloc[0]
one_time_value = one_time_shares * df['close'].iloc[-1]
one_time_profit = one_time_value - result['total_invested']
one_time_profit_rate = (one_time_profit / result['total_invested']) * 100 if result['total_invested'] > 0 else 0
print(f"一次性买入收益: {one_time_profit:.2f} 元 ({one_time_profit_rate:.2f}%)")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

ax1.plot(df.index, df['close'], label='收盘价', linewidth=1.5, color='blue')
if len(result['investment_dates']) > 0:
    dates = [x['date'] for x in result['investment_dates']]
    prices = [x['price'] for x in result['investment_dates']]
    ax1.scatter(dates, prices, color='red', s=50, zorder=5, label='定投日')
ax1.set_title('青农商行(002958) 价格走势与定投点', fontsize=14, fontweight='bold')
ax1.set_ylabel('价格 (元)', fontsize=12)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

portfolio_values = []
total_invested_list = []
profit_list = []
annualized_return_list = []
current_shares = 0
current_invested = 0
invest_dict = {x['date']: x['shares'] for x in result['investment_dates']}
date_to_profit = {}
date_to_annualized_return = {}

start_date = df.index[0]

for date in df.index:
    if date in invest_dict:
        current_shares += invest_dict[date]
        current_invested += monthly_investment
    value = current_shares * df.loc[date, 'close']
    profit = value - current_invested
    
    # 计算年化收益率
    days = (date - start_date).days
    annualized_return = 0.0
    if days > 0 and current_invested > 0:
        years = days / 365.25
        if value > 0:
            annualized_return = ((value / current_invested) ** (1 / years) - 1) * 100
    
    portfolio_values.append(value)
    total_invested_list.append(current_invested)
    profit_list.append(profit)
    annualized_return_list.append(annualized_return)
    date_to_profit[date] = profit
    date_to_annualized_return[date] = annualized_return

ax2.plot(df.index, portfolio_values, label='资产市值', linewidth=2, color='green')
ax2.plot(df.index, total_invested_list, label='累计投入', linewidth=2, color='orange', linestyle='--')
ax2.set_title('定投资产净值变化', fontsize=14, fontweight='bold')
ax2.set_xlabel('日期', fontsize=12)
ax2.set_ylabel('金额 (元)', fontsize=12)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

def format_coord(x, y):
    try:
        # 将 Matplotlib 的内部数值转换为日期对象
        date_obj = mdates.num2date(x)
        date_str = date_obj.strftime('%Y-%m-%d')
        
        # 尝试寻找最接近的实际交易日数据
        target_date = pd.Timestamp(date_obj).replace(tzinfo=None) # 去除时区以匹配索引
        nearest_date = df.index.asof(target_date)
        
        if nearest_date is not pd.NaT:
            price = df.loc[nearest_date, 'close']
            profit = date_to_profit[nearest_date]
            annualized_return = date_to_annualized_return[nearest_date]
            profit_color = '+' if profit >= 0 else ''
            annualized_color = '+' if annualized_return >= 0 else ''
            return f'日期: {date_str} | 收盘价: {price:.2f}元 | 盈亏: {profit_color}{profit:.2f}元 | 年化: {annualized_color}{annualized_return:.2f}% | 当前y轴: {y:.2f}'
        return f'日期: {date_str} | y: {y:.2f}'
    except:
        return f'x={x:.4f}, y={y:.2f}'

# 重新绑定
ax1.format_coord = format_coord
ax2.format_coord = format_coord

plt.tight_layout()
plt.savefig('sip_backtest_result.png', dpi=300, bbox_inches='tight')
print("\n回测图表已保存为: sip_backtest_result.png")
print("\n提示: 在价格走势或资产净值图表上，鼠标悬停在坐标区域即可查看对应日期的收盘价")
plt.show()

print("\n" + "=" * 60)
print("回测完成！")
print("=" * 60)
