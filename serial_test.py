#!/bin/usr/env python3
import serial
import time
import cv2
import os
import csv
import json
import multiprocessing

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



transData="\r\n149149"
data=""

measuredTime= 0


#always check code running expectedly if changing value of frequency
frequency =20
period=1/frequency

# save data to csv
csv_file = "dataInput.csv"
fieldnames = ['image_path', 'angle', 'speed']

#open json file 

f =open("speed_steer.json")
storageSteerSpeed= json.load(f)
sharedTime= 1

def main(sharedTime,realValueServo,realValueBLDC,sharedFlag):
    global measuredTime
    global transData
 
   
    timeCount = 1 
   
    while True:
        if (sharedFlag.value==1):
            break
        time.sleep(0.001)
    startTime=time.time()
    while True:
        #reset value of variables
        valueBLDC=""
        valueServo=""
         
       
     
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

        # convert value of Servo and BLDC to int for calculating
        valueServo=int(str(valueServo).zfill(3))
        valueBLDC=int(str(valueBLDC).zfill(3))

        if (valueBLDC!=0):
            valueBLDC = map_value(valueBLDC,99,199,129,169)

        
        # convert value of Servo and BLDC to str for transmiting
        # make sure len of trans Data is always 8
        valueServo =str(valueServo).zfill(3)
        valueBLDC= str(valueBLDC).zfill(3) 

        
        # transData, not accepted string "\r\n000000"
        # make sure host cannot transmit value error
        if (valueServo!="000" or valueBLDC!="000"):
            transData= "\r"+"\n" +valueServo+valueBLDC
        compareTime = (time.time()-startTime)/timeCount
        if(compareTime>period):
          
            #transmit data
            stm.write(transData.encode())
            tempTime = round(time.time()-measuredTime,3)
            print(tempTime,"Data: ",transData, round(time.time()-startTime,4),timeCount,"main")    
           

            #convert value PWM of servo and BLDC to real value (degree and cm/s)
            keyServo = transData[2:5]
            keyBLDC = transData[5:8]
            realValueServo.value = round(float(storageSteerSpeed['steer_angle'][keyServo]),2)
            realValueBLDC.value = round(float(storageSteerSpeed['speed'][keyBLDC]),2)
            
            
            

            timeCount+= 1
            
            print('Saved!')
            measuredTime= time.time()

            
        # show image
        # cv2.imshow('Webcam', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break


def capture_camera(sharedTime,realValueServo,realValueBLDC,sharedFlag):
    frameID =0
    timeCount = 1
    # Create output folder
    output_dir = "output_img"
    # Create output fold
    os.makedirs(output_dir, exist_ok=True)

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    # Init video capture
    # if cap not set, cap.read() will be very slow
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS,30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
    if not cap.isOpened():
        raise IOError("dont open webcam")
   
    # time.sleep(5)
    

    sharedFlag.value=1
    startTime=time.time()
    while True:
       
        compareTime = (time.time()-startTime)/timeCount
        if(compareTime>period):
            # print("hi")
            #   take and store a picture
            ret, frame = cap.read()
            if not ret:
                break
            image_path = os.path.join(output_dir, f"frame_{frameID}.jpg")
            cv2.imwrite(image_path, frame)
            
        
            print(round(time.time()-startTime,4),timeCount,"capture_camera",realValueServo.value,realValueBLDC.value) 
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writerow({'image_path': image_path, 'angle': round(realValueServo.value,2), 'speed': round(realValueBLDC.value,2)})
            timeCount+= 1
            frameID += 1

def map_value(val, in_min, in_max, out_min, out_max):
    return int((val-in_min)*(out_max-out_min)/(in_max-in_min)+out_min)


def test_speed():
   
    transData= "\r"+"\n" +"149"+ "129"
        
    stm.write(transData.encode())
    print(round(time.time()-measuredTime,3),"Data: ",transData)  
    time.sleep(1)
      

    transData= "\r"+"\n" +"149"+ "149"
    stm.write(transData.encode())
    print(round(time.time()-measuredTime,3),"Data: ",transData)  
    time.sleep(20)

    # transData= "\r"+"\n" +"149"+ "159"
    # stm.write(transData.encode())
    # print(round(time.time()-measuredTime,3),"Data: ",transData)  
    # time.sleep(2)

    # transData= "\r"+"\n" +"149"+ "149"
    # stm.write(transData.encode())
    # print(round(time.time()-measuredTime,3),"Data: ",transData)  
    # time.sleep(5)
    

if __name__=="__main__":
    

   


    
    
    sharedTime = multiprocessing.Value('f')
    realValueServo = multiprocessing.Value('f')
    realValueBLDC = multiprocessing.Value('f')
    sharedFlag =multiprocessing.Value('i')
    sharedFlag.value=0
    # capture_camera(sharedTime,realValueServo,realValueBLDC,sharedFlag)
    # main(sharedTime,realValueServo,realValueBLDC,sharedFlag)
    t1 = multiprocessing.Process(target=main,args=(sharedTime,realValueServo,realValueBLDC,sharedFlag))
    t2 = multiprocessing.Process(target=capture_camera,args=(sharedTime,realValueServo,realValueBLDC,sharedFlag))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("hello")
 