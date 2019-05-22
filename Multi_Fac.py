# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 19:14:58 2018

@author: shixr
"""
from __future__ import division
import os
import sys
stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr 
reload(sys)
sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde 
sys.setdefaultencoding('utf-8')
print (sys.getdefaultencoding())
import datetime
import matplotlib.pyplot as plt
plt.style.use( 'ggplot')
plt.rcParams[ 'font.sans-serif'] = 'Microsoft YaHei'
plt.rcParams[ 'axes.unicode_minus'] = False
import warnings
warnings.filterwarnings("ignore")
import pythoncom
pythoncom.CoInitialize()
sys.path.append(r'D:\Code\DataProc')
#sys.path.append(r'D:\shixr\Code\Functions')
sys.path.append(r'D:\Code\Functions')

import BasicInfo
from MultiFactorProcessFun import MultiFactorProcess
#------------------------------Path-----------------------------------------
whoespath = 'LXM'
info = BasicInfo.GetBasicInfo(whoespath)
if whoespath == 'SXR':
    ModulePath = r'D:\shixr\Code\Trading'

    ResultPath = os.path.join(info.loc['Value','Output_path'],'Trading')
    BarraAlphafacdatapath = info.loc['Value','Barrafac_path']
    BasicDataPath = info.loc['Value','Factor_path']
    StockListPath = os.path.join(info.loc['Value','Output_path'],'Opt')

elif whoespath == 'LXM':
    ModulePath = r'D:\Code\Trading'
    ResultPath = os.path.join(info.loc['Value','Output_path'],'Trading')
    BarraAlphafacdatapath = info.loc['Value','Barrafac_path']
    BasicDataPath = info.loc['Value','Factor_path']
    StockListPath = os.path.join(info.loc['Value','Output_path'],'Opt')
#--------------------------------------------------------------------------
#------------------------------Para----------------------------------------
st_dt = datetime.date(2011,1,1)

end_dt = datetime.date(2019,5,17)
Prefix = 'CNE5S_100_Asset_Exposure_CNE5S_'

valueset     = ['PB',Prefix + 'EARNYILD','PETTM','PSTTM']
growthset    = [Prefix + 'GROWTH','YOYROE','S_QFA_YOYSALES','S_QFA_YOYOP','DELTA_S_QFA_ROE_DEDUCTED'] #
volset       = [Prefix + 'RESVOL','BIT']
mrktset      = [Prefix + 'LIQUIDTY','TO-Norm','Skew20','Gamble','TO-FREE','ILLIQ','TurnOver1M','BIAS60'] #
AlphaFacNameList = valueset + growthset + volset + mrktset
InputAlphaFacWeight = []

'''
divw_initialinput =  0.005 for CSI500
divw_initialinput =  0.02  for HS300
单独控制证券二级行业，填165
MultiFactorProcess(whoespathinput = 'LXM',\ #路径参数
begindateinput = st_dt,\ #起始时间 IFFP 为False时默认时间为2015,1,5
enddateinput = end_dt,\ #截止时间
base_idxinput = '300',\ #优化器benchmark,回溯benchmark
respec_Ind_Lev2_input = [],\ #对某个二级行业进行单独控制，二级中信行业序号
merge_pool_input = [],\ #将数据在初始时使用某个股票池进行切割 Quantamental、300Weight
InputAlphaFacWeight = [],\ #输入Alpha因子权重，需要在函数内部修改加权方式参数才起作用，目前不起作用
AlphaFacNameList = AlphaFacNameList,\ #Alpha因子列表
stockpoolinput = '300Weight',\ #选股池
IFFP = False,\ #是否运行因子处理部分，True时运行完整代码并且储存中间变量，False时读取中间变量运行，注意时间匹配目前
               #目前默认时间为 startdate:2015,1,5
IfMakeLatestStockListinput = False,\ #True时只生成最新的一期的选股结果
divw_initialinput = 0.02) # 个股权重相对基准偏离上限
'''


#order_input,optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
#    begindateinput = st_dt,\
#    enddateinput = end_dt,\
#    base_idxinput = '300',\
#    respec_Ind_Lev2_input = [165,],\
#    merge_pool_input = [],\
#    InputAlphaFacWeight = [],\
#    AlphaFacNameList = AlphaFacNameList,\
#    stockpoolinput = '300Weight',\
#    IFFP = True,\
#    IfMakeLatestStockListinput = False,\
#    divw_initialinput = 0.02)


#order_input,optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
#    begindateinput = st_dt,\
#    enddateinput = end_dt,\
#    base_idxinput = '300',\
#    respec_Ind_Lev2_input = [],\
#    merge_pool_input = [],\
#    InputAlphaFacWeight = [],\
#    AlphaFacNameList = AlphaFacNameList,\
#    stockpoolinput = '800Weight',\
#    IFFP = True,\
#    IfMakeLatestStockListinput = False,\
#    divw_initialinput = 0.02)


#order_input,optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
#    begindateinput = st_dt,\
#    enddateinput = end_dt,\
#    base_idxinput = '500',\
#    respec_Ind_Lev2_input = [],\
#    merge_pool_input = [],\
#    InputAlphaFacWeight = [],\
#    AlphaFacNameList = AlphaFacNameList,\
#    stockpoolinput = '500Weight',\
#    IFFP = True,\
#    IfMakeLatestStockListinput = False,\
#    divw_initialinput = 0.005)


    
order_input,optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
    begindateinput = st_dt,\
    enddateinput = end_dt,\
    base_idxinput = '500',\
    respec_Ind_Lev2_input = [],\
    merge_pool_input = [],\
    InputAlphaFacWeight = [],\
    AlphaFacNameList = AlphaFacNameList,\
    stockpoolinput = 'Quantamental',\
    IFFP = True,\
    IfMakeLatestStockListinput = False,\
    divw_initialinput = 0.005)



#order_input,optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
#    begindateinput = st_dt,\
#    enddateinput = end_dt,\
#    base_idxinput = '1000',\
#    respec_Ind_Lev2_input = [],\
#    merge_pool_input = [],\
#    InputAlphaFacWeight = [],\
#    AlphaFacNameList = AlphaFacNameList,\
#    stockpoolinput = 'Quantamental',\
#    IFFP = True,\
#    IfMakeLatestStockListinput = False,\
#    divw_initialinput = 0.005)
