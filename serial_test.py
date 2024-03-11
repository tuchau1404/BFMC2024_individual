#!/bin/usr/env python3
import serial
import time
stm = serial.Serial(
port = "/dev/ttyACM0",
baudrate = 115200,
bytesize = serial.EIGHTBITS, 
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE, 
timeout = 1,
xonxoff = False,
rtscts = True,
dsrdtr = True,
writeTimeout = 2
)
flag_start=0
flag_servo=1
flag_BLDC=1
count =1
transData =""
validTransData="\r\n149149"
data=""
measuredTime= 0
#always check code running expectedly if changing value of frequency
frequency =40
period=1/frequency
def main():

    #reset value of variables
        
    valueBLDC=""
    valueServo=""
    transData=""
    global measuredTime
    global validTransData
    # detecting first and second character of received data
    data =stm.read().decode('ascii')
    if (data=="\n" ):
        for i in range(3):
            data =stm.read().decode('ascii')
            if(data=='\0'):
                valueServo="0"+valueServo
                continue
            valueServo +=str(data)
        for i in range(3):
            
            data =stm.read().decode('ascii')
            if (data=='\0'):
                valueBLDC="0"+valueBLDC
                continue
            valueBLDC +=str(data)
    
    #make sure len of trans Data is always 8
    transData="\r"+"\n"+str(valueServo).zfill(3)+str(valueBLDC).zfill(3)    
    
    # trans Data, not accepted string "\r\n000000"
    if (transData !="\r\n000000"):
        validTransData=transData
    if((time.time()-measuredTime)>period):
        
        stm.write(validTransData.encode())
        print(round(time.time()-measuredTime,3),"Data: ",validTransData)
        measuredTime= time.time()
        

    
    
    

while True:
    main()
