import os
import pandas as pd

def get_orders(path_start, path_end, factor):
    files = os.listdir(path_start)
    for file in files:
        df2 = pd.read_csv(path_start + '/' + file, index_col=0)
        df2.index = pd.to_datetime(df2.index).values.astype('datetime64[D]')
        # 产生信号
        for i in range(1, len(df2.index)):
            if df2.loc[df2.index[i], factor] > df2.loc[df2.index[i-1], factor]:
                df2.loc[df2.index[i], 'signal'] = 1
            elif df2.loc[df2.index[i], factor] < df2.loc[df2.index[i-1], factor]:
                df2.loc[df2.index[i], 'signal'] = -1
            else:
                df2.loc[df2.index[i], 'signal'] = 0
        df2.dropna(axis=0, inplace=True)

        df2[['收盘', 'signal']].to_csv(\
            path_end + '/' + file[:-4] + '_' + factor + '.csv')

get_orders('./factors', './signals', 'vnsp_llt')