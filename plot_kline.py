import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib import font_manager
import platform

print("正在读取数据...")

system_name = platform.system()
if system_name == 'Windows':
    font_names = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong', 'KaiTi']
    found = False
    for font_name in font_names:
        try:
            font_prop = font_manager.FontProperties(family=font_name)
            plt.rcParams['font.sans-serif'] = [font_name]
            plt.rcParams['axes.unicode_minus'] = False
            print(f"使用字体: {font_name}")
            found = True
            break
        except:
            continue
    if not found:
        print("未找到中文字体，使用默认字体")
elif system_name == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC']
    plt.rcParams['axes.unicode_minus'] = False
else:
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('qrcb_historical_data.csv')

df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

df = df.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'amount': 'Volume'
})

print(f"数据范围: {df.index[0]} 至 {df.index[-1]}")
print(f"共 {len(df)} 条记录")

recent_df = df.tail(100)

print("\n正在绘制K线图...")

mc = mpf.make_marketcolors(
    up='red',
    down='green',
    edge='i',
    wick='i',
    volume='in',
    inherit=True
)

# 1. 先确定当前系统可用的字体名称
if system_name == 'Windows':
    my_font = 'SimHei'
elif system_name == 'Darwin':
    my_font = 'Arial Unicode MS'
else:
    my_font = 'WenQuanYi Micro Hei'

# 2. 在创建样式时，明确指定 rc 参数
s = mpf.make_mpf_style(
    marketcolors=mc,
    gridaxis='both',
    gridstyle='-.',
    y_on_right=False,
    figcolor='white',
    facecolor='white',
    # 核心修正：通过 rc 字典传递字体和负号设置
    rc={
        'font.family': my_font, 
        'axes.unicode_minus': False
    }
)

# 3. 如果你的标题包含中文，请确保字符串正确
# 例如：title='青农商行 (002958) 历史K线图'

fig, axes = mpf.plot(
    recent_df,
    type='candle',
    style=s,
    title='青农商行 (002958) K线图 (最近 100 天)',
    ylabel='价格',
    volume=True,
    ylabel_lower='交易量',
    figratio=(16, 9),
    figscale=1.2,
    returnfig=True
)

plt.savefig('qrcb_kline.png', dpi=300, bbox_inches='tight')
print("K线图已保存为: qrcb_kline.png")

mpf.show()
