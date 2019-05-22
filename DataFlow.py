# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 19:14:58 2018

@author: LXM
"""
from __future__ import unicode_literals
from __future__ import division
import numpy as np
import pandas as pd
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'  #解决Oracle不能输出中文问题
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
from threading import Timer
import ftplib,socket
import zipfile
import warnings
warnings.filterwarnings("ignore")
import win32com.client as win32
import pythoncom
pythoncom.CoInitialize()
sys.path.append(r'D:\Code\DataProc')
#sys.path.append(r'D:\shixr\Code\Functions')
sys.path.append(r'D:\Code\Functions')

from QM_Fetch_Data_fun import QM_Fetch_Data_Fun
from Fetch_CSIDB_fun import FetchCSIDB
import BasicInfo
from MultiFactorProcessFun import MultiFactorProcess
from Order_Generator import Order_Generator_Func 
from WeightedOrderGeneratorFromGZB_v2 import MakeHSInstruction
#from InInfo_fun import InInfo
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
MoneySLinput300 = 3300000
MoneySLinput500 = 3300000

def connect():
    try:
        ftp = ftplib.FTP(HOST)
        ftp.login(user,password)#登录，参数user，password，acct均是可选参数，
         #f.login(user="user", passwd="password")
        return ftp
    except (socket.error,socket.gaierror):
        print("FTP登陆失败，请检查主机号、用户名、密码是否正确")
        sys.exit(0)
    print('已连接到： "%s"' % HOST)
    
def find(ftp,filename):
    ftp_f_list = ftp.nlst()  #获取目录下文件、文件夹列表
    if filename in ftp_f_list:
        return True
    else:
        return False
        
def autogatftpdataextract(HOST,user,password,ftpupfilename,local_path,ftptargetfilename):
    ftp = connect()                  #连接登陆ftp
    dirpath = ftpupfilename   
    ftp.cwd(dirpath)  
    ftp.pwd()
    IfTargetFileExist = find(ftp,ftptargetfilename)
    if not IfTargetFileExist:
        return       
    file_name = ftptargetfilename
    ftp_path =  r'/' + ftpupfilename + ftptargetfilename
    file_handler = open(os.path.join(local_path,file_name), 'wb' )
    ftp.retrbinary("RETR %s"%(ftp_path),file_handler.write)
    file_handler.close()
    f = zipfile.ZipFile(os.path.join(local_path,file_name),'r')
    for file in f.namelist():
        f.extract(file,os.path.join(local_path,ftptargetfilename.strip('.zip')))
    f.close()
    ftp.quit()
    
def code_fill(x):
    #将股票数字代码转为Wind代码
    x_str = str(x).zfill(6)
    if x_str.startswith('0') or x_str.startswith('3'):
        return '.'.join([x_str,'SZ'])
    elif x_str.startswith('6'):
        return '.'.join([x_str,'SH'])
    else:
        return np.nan

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
    
def sendmail(subinput,bodyinput,IfAttachAdress,AttachAdressinput,receiversinput):
    sub = subinput
    body = bodyinput
    outlook = win32.Dispatch('outlook.application')
    receivers = receiversinput
    mail = outlook.CreateItem(0)
    mail.To = receivers[0]
    mail.Subject = sub.decode('utf-8')
    mail.Body = body.decode('utf-8')
    if IfAttachAdress:
        for Aind,Att in enumerate(AttachAdressinput):
            mail.Attachments.Add(AttachAdressinput[Aind])
    mail.Send()    
    
def StratgeGenrator():
    global count
    global sched_time
    global sched_time_NextDay
    global HOST
    global user
    global password
    global ResultPath
    global StockListPath
    global BasicDataPath
    global MoneySLinput300
    global MoneySLinput500
    pythoncom.CoInitialize()
    count = count + 1
    now = datetime.datetime.now()
    T = Timer(300,StratgeGenrator)
    T.start()
    if (not os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5S_100_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&(now>sched_time_NextDay):
        autogatftpdataextract(HOST,user,password,ftpupfilename = 'bime/',\
                  local_path = local_path_Barra,\
                  ftptargetfilename = 'SMD_CNE5S_100_'\
                                    + sched_time.strftime('%Y%m%d')[2:] +'.zip')
        print('1')
    if (not os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5_LOCALID_ID_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&(now>sched_time_NextDay):
        autogatftpdataextract(HOST,user,password,ftpupfilename = 'bime/',\
                  local_path = local_path_Barra,\
                  ftptargetfilename = 'SMD_CNE5_LOCALID_ID_'\
                                    + sched_time.strftime('%Y%m%d')[2:]+'.zip')    
        print('2')
    if (not os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5S_100_UnadjCov_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&(now>sched_time_NextDay):
        autogatftpdataextract(HOST,user,password,ftpupfilename = 'bime/',\
                  local_path = local_path_Barra,\
                  ftptargetfilename = 'SMD_CNE5S_100_UnadjCov_'\
                                    + sched_time.strftime('%Y%m%d')[2:]+'.zip')     
        print('3')
    if (not os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5_Market_Data_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&(now>sched_time_NextDay):
        autogatftpdataextract(HOST,user,password,ftpupfilename = 'cne5/',\
                  local_path = local_path_Barra,\
                  ftptargetfilename = 'SMD_CNE5_Market_Data_'\
                                    + sched_time.strftime('%Y%m%d')[2:]+'.zip')     
        print('4')
    if (os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5S_100_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&\
       (os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5_LOCALID_ID_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&\
       (os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5S_100_UnadjCov_'\
                                    + sched_time.strftime('%Y%m%d')[2:])))&\
       (os.path.exists(os.path.join(local_path_Barra,'SMD_CNE5_Market_Data_'\
                                    + sched_time.strftime('%Y%m%d')[2:]))):
       T.cancel()
       print('BarraFtpCopyDone')
       if os.path.exists(os.path.join(BasicDataPath,sched_time.strftime('%Y%m%d'))):
           
           UpdateComStr = ('D:\Code\Functions\QM_Update_Data_fun.py')
           execfile(UpdateComStr)
           os.rmdir(os.path.join(BasicDataPath,sched_time.strftime('%Y%m%d')))
           Prefix = 'CNE5S_100_Asset_Exposure_CNE5S_'
           valueset     = ['PB',Prefix + 'EARNYILD','PETTM','PSTTM']
           valuewt      = [0.15,0.15               ,0.3    ,0.15   ,0.15    , 0.1]
           growthset    = [Prefix + 'GROWTH','YOYROE','S_QFA_YOYSALES','S_QFA_YOYOP','DELTA_S_QFA_ROE_DEDUCTED']
           #growthset    = [Prefix + 'GROWTH','YOYROE','YOYOR','YOYOP']
           growthwt     = [0.3              ,0.2     ,0.2    ,0.2]
           #volset       = [Prefix + 'RESVOL','BIT']
           volset       = [Prefix + 'RESVOL','BIT']
           volwt        = [0.4              ,0.6]
           mrktset      = [Prefix + 'LIQUIDTY','TO-Norm','Skew20','Gamble','TO-FREE','ILLIQ','TurnOver1M','BIAS60']
           mrktwt       = [0.25                ,0.25    ,0.15    ,0.15    ,0.2]    
           AlphaFacNameList500 = valueset + growthset + volset + mrktset
           InputAlphaFacWeight500 = [0.1,0.2,0.05,0.04,0.06,0.8,0.4,0.06,0.07]
           InputAlphaFacWeight500 = []
           #InputAlphaFacWeight = [0.2*x for x in valuewt] + [0.2*x for x in growthwt] +\
           #                      [0.3*x for x in volwt] + [0.3*x for x in mrktwt]
           csi500_order_input,csi500_optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
                                    begindateinput = datetime.date(2015,1,5),enddateinput =\
           datetime.date(sched_time.year,sched_time.month,sched_time.day),base_idxinput = '500',\
           respec_Ind_Lev2_input = [],merge_pool_input = 'Quantamental',\
           InputAlphaFacWeight = InputAlphaFacWeight500,AlphaFacNameList = AlphaFacNameList500,\
           stockpoolinput = '500Weight',IFFP = True,IfMakeLatestStockListinput = False,divw_initialinput = 0.005)
          
           valueset     = ['PB',Prefix + 'EARNYILD','PETTM','PSTTM']
           valuewt      = [0.15,0.15               ,0.3    ,0.15   ,0.15    , 0.1]
           growthset    = [Prefix + 'GROWTH','YOYROE','S_QFA_YOYSALES','S_QFA_YOYOP','DELTA_S_QFA_ROE_DEDUCTED']
           #growthset    = [Prefix + 'GROWTH','YOYROE','YOYOR','YOYOP']
           growthwt     = [0.3              ,0.2     ,0.2    ,0.2]
           #volset       = [Prefix + 'RESVOL','BIT']
           volset       = [Prefix + 'RESVOL', 'BIT']
           volwt        = [0.4              ,0.6]
           mrktset      = [Prefix + 'LIQUIDTY','TO-Norm','Skew20','Gamble','TO-FREE','ILLIQ','TurnOver1M','BIAS60']
           mrktwt       = [0.25                ,0.25    ,0.15    ,0.15    ,0.2]    
           AlphaFacNameList300 = valueset + growthset + volset + mrktset
           InputAlphaFacWeight300 = [0.1,0.2,0.05,0.04,0.06,0.8,0.4,0.06,0.07]
           InputAlphaFacWeight300 = []
           #InputAlphaFacWeight = [0.2*x for x in valuewt] + [0.2*x for x in growthwt] +\
               #                      [0.3*x for x in volwt] + [0.3*x for x in mrktwt]   
               # respec_Ind_Lev2_input  = [165,166,167] 对证券、保险、信托分别控制
           hs300_order_input,hs300_optfaild_date = MultiFactorProcess(whoespathinput = 'LXM',\
            begindateinput = datetime.date(2015,1,5),enddateinput =\
           datetime.date(sched_time.year,sched_time.month,sched_time.day),base_idxinput = '300',\
           respec_Ind_Lev2_input = [],merge_pool_input = 'Quantamental',\
           InputAlphaFacWeight = InputAlphaFacWeight300,AlphaFacNameList = AlphaFacNameList300,\
           stockpoolinput = '300Weight',IFFP = True,IfMakeLatestStockListinput = False,divw_initialinput = 0.02)
           
           StockListFileListtoday = [csi500_order_input,hs300_order_input]
           for ind,SL in enumerate(StockListFileListtoday):
               print(SL)
               print(ind)
               if ind == 0:
#                   output500path = Order_Generator_Func(MoneySLinput500,Dirct=1,\
#                                                        InputType = 'StockList',MoneyThresh = 3000,\
#                                                        StockListName = SL,whoespath = whoespath,N = 1)
                   output500path,Info1,count,GroupBuyCap,GroupsellCap = MakeHSInstruction (MoneySLinput500,\
                                           [SL],MoneyThresh = 1000,Potweight = [1,],\
                                           IfDropMoneyThresh = True,GZBFileName = 'GZBEmpty',IFSwitch = False,N=1,\
                                           IFFromeGZB = False,PotfoName = 'QM',\
                                           Predict500ExcelFile = '',SplitThresh = 1000000)

                   subinput500 = sched_time_NextDay.strftime('%Y%m%d') + ' CSI500_Strategy_O32_Order'
                   bodyinput500 = 'CSI500 Opt failed Dates:' + str(csi500_optfaild_date)
                   AttachAdressinput500Buy = output500path
                   receiversinput1 = ['liuxm01@piccamc.com']
                   receiversinput2 = ['shixr@piccamc.com']
                   try:
                       sendmail(subinput500,bodyinput500,True,AttachAdressinput500Buy,receiversinput1)
                       sendmail(subinput500,bodyinput500,True,AttachAdressinput500Buy,receiversinput2)
                   except:
                       sendmail('CSI500 enhance All Done except sending mail',\
                                'CSI500 enhance All Done except sending mail',False,\
                                AttachAdressinput500Buy,receiversinput1)
                       sendmail('CSI500 enhance All Done except sending mail',\
                                'CSI500 enhance All Done except sending mail',False,\
                                AttachAdressinput500Buy,receiversinput2)
               else:
                   output300path,Info1,count,GroupBuyCap,GroupsellCap = MakeHSInstruction (MoneySLinput300,\
                                           [SL],MoneyThresh = 1000,Potweight = [1,],\
                                           IfDropMoneyThresh = True,GZBFileName = 'GZBEmpty',IFSwitch = False,N=1,\
                                           IFFromeGZB = False,PotfoName = 'QM',\
                                           Predict500ExcelFile = '',SplitThresh = 1000000)
                   subinput300 = sched_time_NextDay.strftime('%Y%m%d') + ' HS300_Strategy_O32_Order'
                   bodyinput300 = 'HS300 Opt failed Dates:' + str(hs300_optfaild_date)

                   AttachAdressinput300Buy = output300path
                   receiversinput1 = ['liuxm01@piccamc.com']
                   receiversinput2 = ['shixr@piccamc.com']
                   pythoncom.CoInitialize()
                   try:
                       sendmail(subinput300,bodyinput300,True,AttachAdressinput300Buy,receiversinput1)
                       sendmail(subinput300,bodyinput300,True,AttachAdressinput300Buy,receiversinput2)
                   except:
                       sendmail('HS300 enhance All Done except sending mail',\
                                'HS300 enhance All Done except sending mail',False,\
                                AttachAdressinput500Buy,receiversinput1)
                       sendmail('HS300 enhance All Done except sending mail',\
                                'HS300 enhance All Done except sending mail',False,\
                                AttachAdressinput500Buy,receiversinput2)
                    
count = 0
HOST = 'ftp.barra.com'  #FTP主机
user = "uhfynaix"
password = "S1yyoswuuuqfl<"
local_path_Barra = r'D:\Data\Barra\FTP_NEWData'
LocalOldFiles = os.listdir(local_path_Barra)
LocalOldFilesSX = [x for x in LocalOldFiles if (len(x) == 20)&(x[:-7] == 'SMD_CNE5S_100')]
LocalOldFilesSXLastDates = np.max([int('20'+x[-6:]) for x in LocalOldFilesSX ])
BenchDate = pd.read_csv(os.path.join(BasicDataPath,'AShareCalendar.csv'))
TodayTraDate = str(BenchDate.iloc[BenchDate[(BenchDate==LocalOldFilesSXLastDates)\
                                           .values].index.values + 1].values[0][0])
NextTraDate = str(BenchDate.iloc[BenchDate[(BenchDate==LocalOldFilesSXLastDates)\
                                           .values].index.values + 2].values[0][0])
sched_timeBarraToday = datetime.datetime(int(TodayTraDate[:-4]), int(TodayTraDate[-4:-2]),\
                                    int(TodayTraDate[-2:]), 5, 30, 0)
sched_timeBarraNextDay = datetime.datetime(int(NextTraDate[:-4]), int(NextTraDate[-4:-2]),\
                                    int(NextTraDate[-2:]), 5, 30, 0)
sched_time = sched_timeBarraToday
sched_time_NextDay = sched_timeBarraNextDay
nowtime0 = datetime.datetime.now()+datetime.timedelta(days=1)
nowforward2 =  datetime.datetime.now()+datetime.timedelta(days=2)
nowforward2format = int(nowforward2.strftime("%Y%m%d"))
receiversinput1 = ['liuxm01@piccamc.com']
receiversinput2 = ['shixr@piccamc.com']
if nowforward2format in BenchDate['date'].tolist():
    if str(BenchDate['date'].tolist()[BenchDate['date'].tolist().index(nowforward2format)-1])[4:6]\
        != str(nowforward2format)[4:6]:
            sendmail('Remember to login Wind on Remote Servicer Tomorrow!',\
                     'Remember to login Wind on Remote Servicer to Download Index Weight Tomorrow!',False,\
                     [],receiversinput1)
            sendmail('Remember to login Wind on Remote Servicer Tomorrow!',\
                     'Remember to login Wind on Remote Servicer to Download Index Weight Tomorrow!',False,\
                     [],receiversinput2)
    
nowtime0nextformat = int(nowtime0.strftime("%Y%m%d"))
if nowtime0nextformat in BenchDate['date'].tolist():
    Timer(300,StratgeGenrator).start()
#--------------------------------------------------------------------------
def GetDataBaseData():
    global count_Basic
    global sched_time_Basic
    global sched_time_NextDay_Basic
    global BasicDataErr
    local_fac_path = 'D:\Data\Factor'
    count_Basic = count_Basic + 1
    now = datetime.datetime.now()
    T = Timer(2500,GetDataBaseData)
    T.start()
    if (BasicDataErr)&(now>sched_time_NextDay_Basic):
        BasicDataErr = QM_Fetch_Data_Fun(datetime.date(sched_time_Basic.year,sched_time_Basic.month,sched_time_Basic.day))
        print('1')
        [CSI500RightOffer,HS300RightOffer] = FetchCSIDB(datetime.date(sched_time_Basic.year,sched_time_Basic.month,sched_time_Basic.day))
        #InInfo(CSI500RightOffer,HS300RightOffer)    
    if (not BasicDataErr):
       T.cancel()
       print('DataBaseDataCopyDone')
       os.mkdir(local_fac_path + '\\' + sched_time_Basic.strftime('%Y%m%d'))          
count_Basic = 0
BasicDataErr = True       
local_path_Barra = 'D:\Data\Barra\FTP_NEWData'
BasicDataPath = r'D:\Data\Factor'
LocalOldFiles = os.listdir(local_path_Barra)
LocalOldFilesSX = [x for x in LocalOldFiles if (len(x) == 20)&(x[:-7] == 'SMD_CNE5S_100')]
LocalOldFilesSXLastDates = np.max([int('20'+x[-6:]) for x in LocalOldFilesSX ])
BenchDate = pd.read_csv(os.path.join(BasicDataPath,'AShareCalendar.csv'))
TodayTraDate = str(BenchDate.iloc[BenchDate[(BenchDate==LocalOldFilesSXLastDates)\
                                           .values].index.values + 1].values[0][0])
NextTraDate = str(BenchDate.iloc[BenchDate[(BenchDate==LocalOldFilesSXLastDates)\
                                           .values].index.values + 2].values[0][0])
sched_timeBarraToday = datetime.datetime(int(TodayTraDate[:-4]), int(TodayTraDate[-4:-2]),\
                                    int(TodayTraDate[-2:]), 3, 30, 0)
sched_timeBarraNextDay = datetime.datetime(int(NextTraDate[:-4]), int(NextTraDate[-4:-2]),\
                                    int(NextTraDate[-2:]), 3, 30, 0)
sched_time_Basic = sched_timeBarraToday
sched_time_NextDay_Basic = sched_timeBarraNextDay
nowtime1 = datetime.datetime.now()+datetime.timedelta(days=1)
nowtime1nextformat = int(nowtime1.strftime("%Y%m%d"))
if nowtime1nextformat in BenchDate['date'].tolist():
    Timer(10,GetDataBaseData).start()
