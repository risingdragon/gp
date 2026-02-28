import akshare as ak
import pandas as pd
import os
import requests
import urllib3
import ssl

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''

original_get = requests.get

def patched_get(*args, **kwargs):
    kwargs['verify'] = False
    return original_get(*args, **kwargs)

requests.get = patched_get

stock_code = "sz002958"

print("正在获取青农商行(sz002958)的历史数据...")

try:
    df = ak.stock_zh_a_hist_tx(symbol=stock_code, start_date="20190101", end_date="20261231", adjust="qfq")
    print(f"数据获取成功！共 {len(df)} 条记录")
    print("\n最后10条数据:")
    print(df.tail(10))
    
    output_file = "qrcb_historical_data.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\n数据已保存到: {output_file}")
except Exception as e:
    print(f"获取数据时出错: {e}")
    import traceback
    traceback.print_exc()
