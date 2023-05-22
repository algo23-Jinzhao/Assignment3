import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 参数
n = 60
d = 60
d_vnsp = 10

def get_factors(path_start, path_end):
    files = os.listdir(path_start)
    for file in files:
        df_data= pd.read_csv(path_start + '/' + file)

        # 最早从2005-01-04开始
        df_data = pd.read_csv(path_start + '/' + file, index_col=0)
        df_data.index = pd.to_datetime(df_data.index).values.astype('datetime64[D]')
        df1 = df_data.loc['2005':].replace(0, np.nan) # 把0替换成nan
        df1.dropna(axis=0, inplace=True) # 删除所有为nan的行

        # 因子构建
        for i in range(n, len(df1.index)-1):
            # 得到i-1到i-n这段的数据, 换手率计算权重
            initial_array = 1 - df1.loc[df1.index[i-n]:df1.index[i-1], '成交均价'] / df1.loc[df1.index[i], '成交均价']
            array_1 = df1.loc[df1.index[i-n]:df1.index[i-1], '换手率']
            array_2 = (1-array_1).iloc[::-1].shift().fillna(1).cumprod().iloc[::-1]
            w_array = array_1 * array_2
            w_array_pct = w_array / w_array.sum()
            gain_loss_array = initial_array * w_array_pct
            gain = 0
            loss = 0
            for j in gain_loss_array:
                if j > 0 :
                    gain += j
                elif j < 0:
                    loss += j
            df1.loc[df1.index[i+1], 'gain'] = gain
            df1.loc[df1.index[i+1], 'loss'] = loss
        df1.dropna(axis=0, inplace=True)

        # 因子平滑化，d越大，延迟越高，曲线越平滑
        def LLT(data, d):
            llt = [(data.iloc[0]+data.iloc[1])/2, (data.iloc[0]+data.iloc[1])/2]
            alpha = 2/(d+1)
            for i in range(2, len(data.index)):
                llt.append((alpha-alpha**2/4)*data.iloc[i] + alpha**2/2*data.iloc[i-1] - (alpha-3*alpha**2/4)*data.iloc[i-2] \
                    + 2*(1-alpha)*llt[i-1] - (1-alpha)**2*llt[i-2])
            return llt

        df1['gain_llt'] = LLT(df1['gain'], d)
        df1['loss_llt'] = LLT(df1['loss'], d)
        df1['vnsp_llt'] = LLT(df1['gain_llt'] + np.square(df1['loss_llt']), d_vnsp)

        df2 = df1.iloc[(d+d_vnsp):, :].copy()

        #绘制第一个Y轴
        fig = plt.figure(figsize=(20,8), dpi=80)
        ax = fig.add_subplot(111)
        lin1 = ax.plot(df2.index, df2['收盘'], label='close price')
        ax.set_ylabel('close price')
        
        #绘制另一Y轴    
        ax1 = ax.twinx()

        lin2 = ax1.plot(df2.index, df2['gain'], label='gain', color='orange')
        lin3 = ax1.plot(df2.index, df2['loss'], label='loss', color='yellow')
        lin4 = ax1.plot(df2.index, df2['gain_llt'], label='gain_llt', color='red')
        lin5 = ax1.plot(df2.index, df2['loss_llt'], label='loss_llt', color='green')
        lin6 = ax1.plot(df2.index, df2['vnsp_llt'], label='vnsp_llt', color='purple')
        ax1.set_ylabel('factor value')
        
        #合并图例
        lins = lin2 + lin3 + lin4 + lin5 + lin6 + lin1
        labs = [l.get_label() for l in lins]
        ax.legend(lins, labs, bbox_to_anchor=(1.05, 0), loc=3, borderaxespad=0, fontsize=15)
        #plt.savefig('./figures/' + file[:-4] + '_factors.png', dpi=600, bbox_inches='tight')
         
        df2.to_csv(path_end + '/' + file)

get_factors('./daily_data', './factors')