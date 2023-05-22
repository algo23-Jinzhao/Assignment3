import akshare as ak
import pandas as pd
import os

# 得到指数信息表
index_stock_info_df = ak.index_stock_info()
index_stock_info_df.to_csv('./IndexInfo.csv', index=0)

# 上证综指（000001.SH）、中证500（000905.SH）、创业板指数（399006.SZ）、中小板指数（399005.SZ）、沪深300指数（000300.SH）

index_code_list = ['000001', '000905', '399006', '399005', '000300']

# 先分析上证综指
df_info = pd.read_csv('./IndexInfo.csv', dtype={'index_code': object})
df_info.set_index('index_code', inplace=True)

def get_data(code):
    index_name = df_info.loc[code, 'display_name']
    df_data = ak.index_zh_a_hist(symbol=code, period="daily", start_date=df_info.loc[code, 'publish_date'])
    df_result = df_data[['日期', '收盘']].copy()
    df_result['换手率'] = df_data['换手率'] / 100
    df_result['成交均价'] = df_data['成交额'] / df_data['成交量']
    df_result.to_csv('./daily_data/' + code + '_' + index_name + '.csv', index=0)

for i in index_code_list:
    get_data(i)