# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 13:34:19 2018

@author: ShiXiaoRan
"""
import sys
stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr 
reload(sys)
sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde 
sys.setdefaultencoding('utf-8')
print (sys.getdefaultencoding())
import os
import numpy as np
import pandas as pd
from WindPy import *
import datetime
import matplotlib.pyplot as plt
plt.style.use( 'ggplot')
plt.rcParams[ 'font.sans-serif'] = 'Microsoft YaHei'
plt.rcParams[ 'axes.unicode_minus'] = False
import matplotlib.gridspec as gridspec
###############################################################
reportdate = '20181230'
fundcode = '004194.OF'
RootPath = r'D:\Data'
GZBpath = r'D:\Code\Trading'
GZBfilename = r'ZZ500IndGZB20181226'
Optpath = r'D:\Output\Opt'
Optfilename = r'Portf_20181226_500_Enhance_12-26_6h36min_20161209_20181225_20_ICIR_ICN_12_Set0_True'
InputType = 'FundIndex' #'Potf' 'GZB' 'FundIndex'
ReportDate = datetime.datetime.strptime(reportdate,"%Y%m%d").date()
ExposureSpecRiskDataPath = os.path.join(RootPath,'Barra','AdjData','SMD_CNE5S_100_D')
FacCovPath = os.path.join(RootPath,'Barra','FTP_NEWData')
ResultPath = os.path.join(RootPath,'Barra','MSCI','PotfolioRiskCal')
def GetType(x):
    try:
        xint = int(x)
        if (len(str(xint)) == 14)&\
        (str(xint)[:4] == '1102'): 
            xout = True
        else:
            xout = False
    except:
        xout = False
    return xout   
def GetBarraData_Barrid(path):
   #读取数据函数，需要列名称行以'!Barrid'开始
    BarradataList = [] 
    Title = []
    if not os.path.isfile(path):
        print('data file not found: \n' + path)
        exit(1)
    with open(path, 'r') as ifs:    
        for line in ifs:
            row=line.strip()
            if (row.startswith('!Barrid')):
                Title = row.split('|')
                Title[0] = Title[0][1:]
            if not ( row.startswith('!') or row.startswith('\n') ):
                columns = row.split('|')
                BarradataList.append(columns)
    BarradataDF = pd.DataFrame(BarradataList,columns=Title)    
    return  BarradataDF  
def GetBarraData_Covariance(path):
   #读取方差、协方差矩阵数据函数，需要列名称行以'!Barrid'开始
    BarradataList = [] 
    Title = []
    if not os.path.isfile(path):
        print('data file not found: \n' + path)
        exit(1)
    with open(path, 'r') as ifs:    
        for line in ifs:
            row=line.strip()
            if (row.startswith('!Factor1')):
                Title = row.split('|')
                Title[0] = Title[0][1:]
            if not ( row.startswith('!') or row.startswith('\n') ):
                columns = row.split('|')
                BarradataList.append(columns)
    BarradataDF = pd.DataFrame(BarradataList,columns=Title)
    BarradataDF = BarradataDF.iloc[:-1,:]
    Facname = list(BarradataDF.drop_duplicates(subset = 'Factor1')['Factor1'])
    FacCov = pd.DataFrame(np.nan*np.zeros([len(Facname),len(Facname)]),index = Facname,columns = Facname)
    for i in BarradataDF.index:
        FacCov.loc[BarradataDF.iloc[i,0],BarradataDF.iloc[i,1]] = BarradataDF.iloc[i,2]
        FacCov.loc[BarradataDF.iloc[i,1],BarradataDF.iloc[i,0]] = BarradataDF.iloc[i,2]    
    return  FacCov      
def code_fill(x):
    #将股票数字代码转为Wind代码
    x_str = str(x)
    if x_str.startswith('0') or x_str.startswith('3'):
        return '.'.join([x_str,'SZ'])
    elif x_str.startswith('6'):
        return '.'.join([x_str,'SH'])
    else:
        return np.nan
def code_fill(x):
    #将股票数字代码转为Wind代码
    x_str = str(x).zfill(6)
    if x_str.startswith('0') or x_str.startswith('3'):
        return '.'.join([x_str,'SZ'])
    elif x_str.startswith('6'):
        return '.'.join([x_str,'SH'])
    else:
        return np.nan
w.start()  
if InputType == 'GZB':
    GZBData = pd.read_excel(os.path.join(GZBpath,GZBfilename + '.xls'))
    GZBData['IsStock'] = pd.DataFrame(GZBData.iloc[:,0]).applymap(lambda x:GetType(x))
    GZBData = GZBData[GZBData['IsStock']]
    GZBData['StockCode'] = pd.DataFrame(GZBData.iloc[:,0]).applymap(lambda x: code_fill(int(str(x)[8:])))
    GZBData['HoldWeight'] = GZBData.iloc[:,7]/np.sum(GZBData.iloc[:,7])
    GZBDataUSE = GZBData.iloc[:,[1,2,7,10,12,13]]
    GZBDataUSE.columns = ['Chinese ID','HoldNum','HoldCap','TradeState','StockCode','HoldWeight']
    PotfolioDatausefull = GZBDataUSE.loc[:,['StockCode','HoldWeight']]
    PotfolioDatausefull.columns =['StockCode','Weight']
    PotfolioDatausefull['Weight'] = PotfolioDatausefull['Weight']*100
    PotfolioDatausefull.reset_index(drop = True,inplace = True)
elif InputType == 'FundIndex' :  
    raw = w.wset("allstockhelddetaill",'rptdate='+reportdate+';windcode='+fundcode)   
    raw_df = pd.DataFrame(raw.Data, index = raw.Fields, columns = raw.Codes).T
    PotfolioDatausefull = raw_df.loc[:,['stock_code','proportiontototalstockinvestments']]
    PotfolioDatausefull.columns =['StockCode','Weight']
else:
    PotfolioDatausefull = pd.read_excel(os.path.join(Optpath,Optfilename + '.xlsx'))
    PotfolioDatausefull['Weight'] = PotfolioDatausefull['Weight'] *100
    PotfolioDatausefull = PotfolioDatausefull.loc[:,['StockCode','Weight']]
print('组合权重值和:'+str(PotfolioDatausefull['Weight'].sum()))
FundNameraw = w.wss(fundcode, "fund_fullname")
FundName = FundNameraw.Data[0][0]
##基准股票指数
#提取指数名称
BenchmarkStrraw = w.wss(fundcode, "fund_benchmark")
BenchmarkStr = BenchmarkStrraw.Data[0][0]
Indexnameset = ['沪深300','中证500','中证1000','中证800']
BenchmarkIndexCode = ['000300.SH','000905.SH','000852.SH','000906.SH']
Indexdict = dict(zip(Indexnameset, BenchmarkIndexCode))
for Indexname in Indexnameset:
    if Indexname in BenchmarkStr:
        benchmarkname = Indexname
        benchmarkindexcode = Indexdict[benchmarkname]
#提取指数权重
benchmarkraw=w.wset("indexconstituent",'date='+reportdate+';windcode='+ benchmarkindexcode)
benchmarkraw_df = pd.DataFrame(benchmarkraw.Data, index = benchmarkraw.Fields, columns = benchmarkraw.Codes).T
benchmarkusefull = benchmarkraw_df.iloc[:,[1,3]]
benchmarkusefull.columns =['StockCode','Weight']
print('基准指数权重值和:'+str(PotfolioDatausefull['Weight'].sum()))        
# 读取FacCov和因子暴露数据
#报告期之前最近的交易日
NearestTradeDate = w.tdaysoffset(0,reportdate, "")
NearestTradeDate = NearestTradeDate.Times
NearestTradeDatestr = NearestTradeDate[0].strftime('%Y%m%d')
#提取方差协方差矩阵
FacCovPath2 = os.path.join(FacCovPath,'SMD_CNE5S_100_'+NearestTradeDatestr[2:])
FacCovraw = GetBarraData_Covariance(os.path.join(FacCovPath2,'CNE5S_100_Covariance.'+NearestTradeDatestr))
##提取因子暴露矩阵
#协方差矩阵因子名称和顺序
FacName = list(FacCovraw)
facExposuredata = pd.DataFrame()
for fan in FacName:
    facExposuredataraw = pd.read_hdf(os.path.join(ExposureSpecRiskDataPath,'CNE5S_100_Asset_Exposure_'+fan+'.hdf5'),key = fan)
    facExposuredataraw = facExposuredataraw.loc[NearestTradeDate,:].T
    facExposuredataraw.columns = [fan]
    facExposuredataraw['StockCode'] = facExposuredataraw.index
    if  len(facExposuredata) == 0 :
        facExposuredata = facExposuredataraw
    else:
        facExposuredata = pd.merge(facExposuredata,facExposuredataraw,how = 'outer',on = 'StockCode')                
#因子暴露矩阵index设为StockCode
facExposuredata.set_index('StockCode',inplace = True)
#因子暴露矩阵因子排列顺序与协方差矩阵一致
facExposuredata = facExposuredata.loc[:,FacName]
#因子暴露矩阵的股票列表和顺序为准
StockCodelist = list(facExposuredata.index)
##提取个股的特质风险数据
SpecRiskdataraw = pd.read_hdf(os.path.join(ExposureSpecRiskDataPath,'CNE5S_100_Asset_Data_SpecRisk%'+'.hdf5'),key = 'SpecRisk%')
SpecRiskdataraw = SpecRiskdataraw.loc[NearestTradeDate,:].T
SpecRiskdataraw.columns = ['SpecRisk']
SpecRiskdataraw['StockCode'] = SpecRiskdataraw.index 
SpecRiskdata = pd.DataFrame(np.nan*np.zeros([len(StockCodelist),1]),index = StockCodelist,columns=['SpecRisk'])
#以StockCodelist为基准给SpecRiskdata赋值
SpecRiskdata.loc[SpecRiskdataraw.loc[SpecRiskdataraw['StockCode'].isin(StockCodelist),'StockCode'],'SpecRisk'] = SpecRiskdataraw.loc[SpecRiskdataraw['StockCode'].isin(StockCodelist),'SpecRisk'].values
#生成SpecVarMatrix矩阵
SpecVarMatrix = pd.DataFrame(np.square(np.diag(list(SpecRiskdata['SpecRisk']))/100),index = StockCodelist,columns = StockCodelist)
#计算组合因子暴露
PotWeightDF = pd.DataFrame(np.zeros([len(StockCodelist),1]),index = StockCodelist,columns = ['Weight'])
PotWeightDF.loc[PotfolioDatausefull.loc[PotfolioDatausefull['StockCode'].isin(StockCodelist),'StockCode'],'Weight'] = PotfolioDatausefull.loc[PotfolioDatausefull['StockCode'].isin(StockCodelist),'Weight'].values
PotWeightDF = PotWeightDF/100
PotfoFacExposure = pd.DataFrame(np.zeros([len(FacName),1]),index = FacName,columns = ['FacExposure'])
PotfoFacExposure['FacExposure'] = (np.dot((PotWeightDF).T.values,facExposuredata.fillna(0).values)).T
#计算基准指数因子暴露
BenchmarkWeightDF = pd.DataFrame(np.zeros([len(StockCodelist),1]),index = StockCodelist,columns = ['Weight'])
BenchmarkWeightDF.loc[benchmarkusefull.loc[benchmarkusefull['StockCode'].isin(StockCodelist),'StockCode'],'Weight'] = benchmarkusefull.loc[benchmarkusefull['StockCode'].isin(StockCodelist),'Weight'].values
BenchmarkWeightDF = BenchmarkWeightDF/100
BenchmarkFacExposure = pd.DataFrame(np.zeros([len(FacName),1]),index = FacName,columns = ['FacExposure'])
BenchmarkFacExposure['FacExposure'] = (np.dot((BenchmarkWeightDF).T.values,facExposuredata.fillna(0).values)).T
##计算组合方差########
FacCovraw = FacCovraw.convert_objects(convert_numeric=True)
##FacCovraw的单位是%^2##
FacCovraw = FacCovraw/10000
PotfoVar=np.nan
PotfoVar = np.float(np.mat(PotWeightDF.T.values)*(np.mat(facExposuredata.fillna(0).values)*np.mat(FacCovraw.fillna(0).values)*np.mat(facExposuredata.fillna(0).T.values) + np.mat(SpecVarMatrix.fillna(0).values))*np.mat(PotWeightDF.values))
BenchMarkVar =  np.float(np.mat(BenchmarkWeightDF.T.values)*(np.mat(facExposuredata.fillna(0).values)*np.mat(FacCovraw.fillna(0).values)*np.mat(facExposuredata.fillna(0).T.values) + np.mat(SpecVarMatrix.fillna(0).values))*np.mat(BenchmarkWeightDF.values))
print('Potfolio\'s variance is'+' '+str(PotfoVar))
########画图#################################
#%matplotlib qt 
#plt.subplot(221)
#idx = np.arange(len(PotfoFacExposure[:10]))
#plt.bar(idx, PotfoFacExposure['FacExposure'][:10].values,width, color='deeppink',alpha = 0.6)
#plt.bar(idx, BenchmarkFacExposure['FacExposure'][:10].values,width,color='blue',alpha = 0.35)
#plt.xticks(idx,map(lambda x: x[6:], PotfoFacExposure.index[:10]), rotation=40,fontsize = 12)
#plt.legend(labels = [fundcode,benchmarkindexcode], loc = 'lower right',fontsize = 13)
#plt.ylabel('Risk Factor Exposure')
#plt.title(headline, fontsize = 20)
#plt.subplot(223)
#idx = np.arange(len(PotfoFacExposure[10:-1]))
#plt.bar(idx, PotfoFacExposure['FacExposure'][10:-1].values,width, color='deeppink',alpha = 0.6)
#plt.bar(idx, BenchmarkFacExposure['FacExposure'][10:-1].values,width,color='blue',alpha = 0.35)
#plt.xticks(idx,map(lambda x: x[6:], PotfoFacExposure.index[10:-1]), rotation=80,fontsize = 11)
#plt.legend(labels = [fundcode,benchmarkindexcode], loc = 'best',fontsize = 13)
#plt.ylabel('Industry Factor Exposure')
#plt.subplot(155)
#plt.show()
#plt.tight_layout()
#plt.savefig(os.path.join(ResultPath,headline + '.png'),dpi = 'figure')
summary = \
'*'*45 + '\n' + \
'Potfolio\'s name is ' +'\n' + \
 FundName + '\n' + \
'Benchmark is ' + benchmarkindexcode + '\n' + \
'Potfolio\'s var is ' + format(PotfoVar, '.3f') + ', std is ' + format(np.sqrt(PotfoVar)*100,'.2f') + '%' + '\n' + \
'Benchmark\'s var is ' + format(BenchMarkVar, '.3f') + ', std is ' + format(np.sqrt(BenchMarkVar)*100,'.2f') + '%' + '\n' + \
'Total holding stock number is ' + str(len(PotfolioDatausefull))+ '\n' + \
'*'*45 
#'Total stock holding proportion is ' + format(raw_df.loc[:,'proportiontonetvalue'].sum(),'.2f')+ '%' + '\n' + \
#'Proportion of top 10 heaviest stock ' + '\n' + \
#'on stock investments is ' + format(np.sum(np.sort(raw_df.loc[:,'proportiontototalstockinvestments'])[-10:]),'.2f')+ '%' + '\n' + \
headline = fundcode +' VS '+ benchmarkindexcode + '_'+reportdate +  '_BarraFacExposure'
width = 0.35
fig =plt.figure(figsize = (13,6.5))
gs = gridspec.GridSpec(nrows=2, ncols=7)
fig.add_subplot(gs[0, 0:6])
idx = np.arange(len(PotfoFacExposure[:10]))
plt.bar(idx, PotfoFacExposure['FacExposure'][:10].values,width, color='deeppink',alpha = 0.6)
plt.bar(idx, BenchmarkFacExposure['FacExposure'][:10].values,width,color='blue',alpha = 0.35)
plt.xticks(idx,map(lambda x: x[6:], PotfoFacExposure.index[:10]), rotation=12,fontsize = 11)
plt.legend(labels = [fundcode,benchmarkindexcode], loc = 'best',fontsize = 13)
plt.ylabel('Risk Factor Exposure')
plt.title(headline, fontsize = 20)
fig.add_subplot(gs[1, 0:7])
idx = np.arange(len(PotfoFacExposure[10:-1]))
plt.bar(idx, PotfoFacExposure['FacExposure'][10:-1].values,width, color='deeppink',alpha = 0.6)
plt.bar(idx, BenchmarkFacExposure['FacExposure'][10:-1].values,width,color='blue',alpha = 0.35)
plt.xticks(idx,map(lambda x: x[6:], PotfoFacExposure.index[10:-1]), rotation=80,fontsize = 11)
plt.legend(labels = [fundcode,benchmarkindexcode], loc = 'best',fontsize = 13)
plt.ylabel('Industry Factor Exposure')
plt.annotate(summary, xy = (0.75,0.74), xycoords = 'figure fraction', fontsize = 12)


