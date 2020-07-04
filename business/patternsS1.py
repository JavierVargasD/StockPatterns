'''
Created on 20/05/2019

@author: JavierMauricioVargas
'''
# Schedule Library imported 
import schedule 
import time
import json
import urllib2
import datetime
import Queue
import smtplib
import socket
from Candle import Candle
from win10toast import ToastNotifier

candleList = []

def ejecuteScript():
    
    now = datetime.datetime.now()
    one_minute = datetime.timedelta(minutes=1) 
    two_minute = datetime.timedelta(minutes=2) 
    one_hour = datetime.timedelta(hours=1) 
    
    now_minus_one = now - one_minute 
    now_minus_two = now - two_minute 
    
    now_minus_one +=  one_hour
    now_minus_two +=  one_hour
    
    now_minus_one_str = str(now_minus_one)[:16]+":00"
    now_minus_two_str = str(now_minus_two)[:16]+":00"
    
    try:

        data = json.load(urllib2.urlopen('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&amp;symbol=FB&amp;interval=1min&amp;apikey=E5KJEEWP24PU8BH7&outputsize=full'))
        timeSeries1min = data['Time Series (1min)']; 
        ticker = data['Meta Data']['2. Symbol']; 
        
        print( "-----")
        candle = Candle(float( timeSeries1min[now_minus_two_str]['1. open'] ), float( timeSeries1min[now_minus_one_str]['4. close'] ), now_minus_one_str )
        global candleList 
        candleList.append(candle)

        print( "o " + str(candle.c_open) + "c " + str(candle.c_close) +" - " + candle.c_id )
        print( candle.getColor() )
        
        sma = 0.0
        
        lastCandlesColor = ""
        
        if len( candleList ) > 19 :
            sma = float(getSMAV2(candleList))
            lastCandlesColor = getLastCandlesColor(candleList)
            candleList.pop(0)
            
        
            
        if candle.getColor() == "R" and  candle.c_open > sma and candle.c_close < sma and lastCandlesColor == "R" :
            print("***************************************** RED RED RED")
            sendEmail(ticker)
            toaster = ToastNotifier()
            toaster.show_toast("MALANGA Alert ! " + ticker)
        elif candle.getColor() == "G" and candle.c_open < sma and candle.c_close > sma and lastCandlesColor == "G" :
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GREEN GREEN GREEN")
            sendEmail(ticker)
            toaster = ToastNotifier()
            toaster.show_toast("MALANGA Alert ! " + ticker)        
        print( "-----")
    except KeyError:
        print("Unreturned key")
        time.sleep(10)
        candleList = getCandlesToSMA()
        ejecuteScript()
        
    except socket.error:
        time.sleep(10)
        candleList = getCandlesToSMA()
        ejecuteScript()
        
    except urllib2.HTTPError:
        time.sleep(10)
        candleList = getCandlesToSMA()
        ejecuteScript()
        
    except urllib2.URLError :
        
        time.sleep(10)
        candleList = getCandlesToSMA()
        ejecuteScript()

    
def initTwoMinutesTimer():
    print("Init 2 minutes timer")
    global candleList
    candleList=[]
    candleList = getCandlesToSMA()
    ejecuteScript()
    schedule.every(2).minutes.do(ejecuteScript) 
    
def getCandlesToSMA():
    
    try:
    
        data = json.load(urllib2.urlopen('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&amp;symbol=FB&amp;interval=1min&amp;apikey=E5KJEEWP24PU8BH7&outputsize=full'))
        
        dataList = data['Time Series (1min)']; 
        
        closeAdding = 0.0
        
        now = datetime.datetime.now() 
        
        now += datetime.timedelta(hours=1) 
        
        j = 3
        
        global candleList
        candleList = []
        
        for x in range( 20 ):
        
            candle = Candle( float( dataList[ str(now - datetime.timedelta(minutes=j-1))[:16]+":00" ]['1. open'] ) , float( dataList[ str(now - datetime.timedelta(minutes=j-2))[:16]+":00" ]['4. close'] ), str(now - datetime.timedelta(minutes=j-2))[:16]+":00" )
            candleList.append(candle)
            
            print( "o " + str(candle.c_open) + "c " + str(candle.c_close) +" - " + candle.c_id )

            j += 2
        
        candleList.pop(0)
        
    except KeyError:
        print("Unreturned SMA key")
        time.sleep(10)
        getCandlesToSMA()
        
    except socket.error:
        time.sleep(10)
        getCandlesToSMA()
        
    except IndexError:
        time.sleep(10)
        getCandlesToSMA()
        
    except urllib2.HTTPError:
        time.sleep(10)
        getCandlesToSMA()
       
    candleList = candleList[::-1]
    return candleList
    

def getSMAV2( candleList ):
    
    closeAdding = 0.0
    
    print("-- GETTING  -- SMA ----")
    
    for i in range( len(candleList) - 1, -1, -1) :
        candle = candleList[i]
        closeAdding += candle.c_close
        print( "o " + str(candle.c_open) + "c " + str(candle.c_close) +" - " + candle.c_id )

    print(str(closeAdding/len(candleList)))
    return str(closeAdding/len(candleList))
    

def getLastCandlesColor( candleList ):
    
    candle1 = candleList[19]
    candle2 = candleList[18]
    candle3 = candleList[17]
    
    if candle1.getColor() == "R" and candle2.getColor() == "R" and candle3.getColor() == "R" :        
        return "R"
    elif candle1.getColor() == "G" and candle2.getColor() == "G" and candle3.getColor() == "G" :
        return "G"
    else :
        return "N"
    

def sendEmail( ticker ):
    
    gmail_user = 'javiervargasd@gmail.com'  
    gmail_password = 'martin2010'
    
    sent_from = gmail_user  
    to = ['javiervargasd@gmail.com']  
    subject = 'MLG alert '  + ticker
    body = 'MLG alert '  + ticker
    
    email_text = """\  
        From: %s  
        To: %s  
        Subject: %s        
        %s
        """ % (sent_from, to, subject, body)
    
    try:  
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
    
        print 'Email sent!'
    except:  
        print 'Something went wrong...'
    
    
    

def mock():
    
    data = json.load(urllib2.urlopen('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&amp;symbol=QCOM&amp;interval=1min&amp;apikey=E5KJEEWP24PU8BH7&outputsize=full'))
    timeSeries1min = data['Time Series (1min)']; 
    ticker = data['Meta Data']['2. Symbol']; 
    
    j = 52
    
    y = 9
    
    ch = "09"
    
    candleList = []
    
    for x in range( 185 ):
        
        curr = str(j)
        curr1 = str(j-1)

           
        if j <= 9  :
            
            curr = "0" + str(j)
            curr1 = "0" + curr1        

        
        elif j == 60:
            curr = "00"
            curr1 = "59"
            j = 0


        if curr1 == "9" : curr1 = "09"
        
        now_minus_two_str = "2019-05-21 "+ch+":"+curr1+":00"
        
        if j == 0:
            y = y + 1
            ch = str(y)
          
        now_minus_one_str = "2019-05-21 "+ch+":"+curr+":00"       

        
        
        print(now_minus_one_str)
        print(now_minus_two_str)
         #getSMA(20, timeSeries1min)
       
        try:
            print( "-----")
            candle = Candle(float( timeSeries1min[now_minus_two_str]['1. open'] ), float( timeSeries1min[now_minus_one_str]['4. close'] ) )
            candleList.append(candle)

            print( "o " + str(candle.c_open) )
            print( "c " + str(candle.c_close) )
            print( candle.getColor() )
            
            sma = 0.0
            
            lastCandlesColor = ""
            
            if len( candleList ) > 19 :
                sma = float(getSMAV2(candleList))
                lastCandlesColor = getLastCandlesColor(candleList)
                candleList.pop(0)
                
            
                
            if candle.getColor() == "R" and  candle.c_open > sma and candle.c_close < sma and lastCandlesColor == "R" :
                print("***************************************** RED RED RED")
                sendEmail(ticker)
                toaster = ToastNotifier()
                toaster.show_toast("MALANGA Alert ! " + ticker)
            elif candle.getColor() == "G" and candle.c_open < sma and candle.c_close > sma and lastCandlesColor == "G" :
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ GREEN GREEN GREEN")
                sendEmail(ticker)
                toaster = ToastNotifier()
                toaster.show_toast("MALANGA Alert ! " + ticker)         
            print( "-----")
        except KeyError:
            print("Unreturned key")

        #time.sleep(2)
                    
        j += 2 
        
#mock()
schedule.every().day.at("10:13:10").do(initTwoMinutesTimer) 

while True: 
    
    schedule.run_pending() 
    time.sleep(1)