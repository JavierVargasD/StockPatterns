'''
Created on 23/05/2019

@author: JavierMauricioVargas
'''

class Candle:
    
    def __init__(self, c_open, c_close, c_id):
        self.c_open = c_open
        self.c_close = c_close
        self.c_id = c_id
        
    c_high=0.0
    c_low=0.0
    

    #Candle color: R=red, G=Green
    def getColor(self):
        
        if self.c_open < self.c_close :
            
            return "G"
        
        elif self.c_open > self.c_close :
            
            return "R"      
            