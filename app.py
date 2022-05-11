from calendar import c
from flask import Flask,request,jsonify,render_template
import os
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import base64
import json
import io
import logging               #import lib for write log
import VMSData
import time
import atexit
from datetime import datetime,timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
#config value
vmswidth = 64
vmsheight = 64
vmsRow= 32
vmsChainLength = 2
vmsParallel = 2
vmsbrightness =20
image = []
CurrentImage =1
BoardVMSID =''
# Configuration for the matrix
options = RGBMatrixOptions()
# options.rows = 32
# options.chain_length = 2
# options.parallel = 2
# options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
# options.gpio_slowdown = 3
# matrix = RGBMatrix(options = options)
# matrix.brightness = vmsbrightness
@app.route("/")
def index():
   return render_template('home.html')
@app.route("/setimage",methods=["POST"])
def setimage():
   global image
   payload = request.form.to_dict(flat = False)
   img = payload["img"][0]#get post json
   #dict_data = json.dumps(json_data)#conver json to dict
   print('-------------------------------')
   VMSData.ClearAllImage()
   ImageID=1
   DisplayOrder =1
   DisplayInterval = 30
   VMSData.InsertImage(ImageID,img, DisplayOrder, DisplayInterval)
   VMSData.ClearAllLastDisplayTime()
   img= base64.b64decode(img)
   #image_file ='stop.bmp'
   #image = Image.open(image_file)
   image_file = io.BytesIO(img)
   image = Image.open(image_file)

   # Make image fit our screen.
   image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
   matrix.SetImage(image.convert('RGB'))
   return "1"
@app.route("/setSetting",methods=["POST"])
def setSetting():
   global image
   try:      
      payload = request.form.to_dict(flat = False)
      width = int(payload["width"][0])
      height = int(payload["height"][0])
      Rows = int(payload["Rows"][0])
      chainlength = int(payload["chainlength"][0])
      parralel = int(payload["parralel"][0])
      brightness = int(payload["brightness"][0])
      #dict_data = json.dumps(json_data)#conver json to dict
      print('-------------------------------')
      VMSData.SetBoardSetting(width, height,Rows,chainlength,parralel,brightness)
   except:
      logging.exception('Got exception on main handler')
   return "1"
@app.route("/getbrightness")
def getbrightness():
   global vmsbrightness
   return  str(vmsbrightness)
@app.route("/setbrightness",methods=["POST"])
def setbrightness():
   global image
   global vmsbrightness
   global matrix
   try: 
      payload = request.form.to_dict(flat = False)
      vmsbrightness = int(payload["brightness"][0])#get post json
      if vmsbrightness < 1: 
         vmsbrightness = 1
      if vmsbrightness >100: 
         vmsbrightness =100
      matrix.brightness = vmsbrightness
      matrix.SetImage(image.convert('RGB'))
      return  str(vmsbrightness)        
   except:
      logging.exception('Got exception on main handler')
   return "-1"   
@app.route("/setMultiImage",methods=["POST"])
def setMultiImage():
   global image
   try:      
      payload = request.form.to_dict(flat = False)
      ImageID = payload["ImageID"][0]
      img = payload["img"][0]#get post json
      DisplayOrder = int(payload["DisplayOrder"][0])
      DisplayInterval = int(payload["DisplayInterval"][0])
      #dict_data = json.dumps(json_data)#conver json to dict
      print('-------------------------------')
      VMSData.InsertImage(ImageID,img, DisplayOrder, DisplayInterval)
      VMSData.ClearAllLastDisplayTime()
      img= base64.b64decode(img)
      #image_file ='stop.bmp'
      #image = Image.open(image_file)
      #image_file = io.BytesIO(img)
      #image = Image.open(image_file)

      # Make image fit our screen.
      # image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
      # matrix.SetImage(image.convert('RGB'))
   except:
      logging.exception('Got exception on main handler')
   return  str(VMSData.GetNumberofDisplayingRecord())     
@app.route("/getcount",methods=["POST"])
def getcount():
   return  str(VMSData.GetNumberofDisplayingRecord())   

@app.route("/clearAll",methods=["POST"])
def clear():
   VMSData.ClearAllImage()
   return "1"

@app.route("/rebootsystem")
def rebootsystem():
   #os.system('sudo reboot') #may be work only on linux
   return "1"

def DoScheduleDisplay():
   global CurrentImage
   global image
   print("Current Image index: "+ str(CurrentImage))
   #CurrentImage =  CurrentImage + 1
   # datetime object containing current date and time
   now = datetime.now()
   print("now =", now)
   # dd/mm/YY H:M:S
   dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
   print("date and time =", dt_string)	
   DisplayingRecord  = VMSData.GetCurrentDisplayingRecord(CurrentImage)
   if len(DisplayingRecord) > 0 :
      #xu ly check hien thi record hien tai
      LastDisplayTimeRow = DisplayingRecord[4]
      print("LastDisplayTimeRow =", LastDisplayTimeRow)	
      if LastDisplayTimeRow =='':
         #bat dau hien thi hinh anh nay
         print("Start Display =", dt_string)	
         VMSData.UpdateLastDisplayTime(CurrentImage,dt_string)
         img = DisplayingRecord[1]
         img= base64.b64decode(img)
         #image_file ='stop.bmp'
         #image = Image.open(image_file)
         image_file = io.BytesIO(img)
         image = Image.open(image_file)

         # Make image fit our screen.
         image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
         matrix.SetImage(image.convert('RGB'))
      else:
         #neu da co thoi gian hien thi thi check xem da qua thoi gian hay chua
         print("neu da co thoi gian hien thi thi check xem da qua thoi gian hay chua")
         print("LastDisplayTimeRow:"+str(LastDisplayTimeRow))
         LastTime = datetime.strptime(LastDisplayTimeRow, '%d/%m/%Y %H:%M:%S')# dd/mm/yy hh:mm:ss
         print("LastTime")
         print(LastTime)
         LastTimeInterval =  timedelta(seconds=int(DisplayingRecord[3])) #don vi tinh : giay
         if(now > LastTime + LastTimeInterval) :   
           
            CurrentImage= CurrentImage+1
            if(CurrentImage > VMSData.GetNumberofDisplayingRecord()):
               CurrentImage = 1
            print("Next Image:" + str(CurrentImage))
            #lấy record tiếp theo ra để hiển thị
            DisplayingRecord  = VMSData.GetCurrentDisplayingRecord(CurrentImage)
            VMSData.UpdateLastDisplayTime(CurrentImage,dt_string)
            img = DisplayingRecord[1]
            img= base64.b64decode(img)
            #image_file ='stop.bmp'
            #image = Image.open(image_file)
            image_file = io.BytesIO(img)
            image = Image.open(image_file)

            # Make image fit our screen.
            image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
            matrix.SetImage(image.convert('RGB'))
   else:    
      print("Not set CurrentLastDisplayTime")
      CurrentImage=1	

if __name__ == "__main__":
   BoardVMSID =''
   print("ClearAllLastDisplayTime")	
   VMSData.ClearAllLastDisplayTime()
   BoardVMSID =VMSData.GetBoardID()
   print(BoardVMSID)
   BoardSetting = VMSData.GetBoardSetting()
   print("BoardSetting")	
   print(BoardSetting)
   vmsRow = int(BoardSetting[3])
   vmsChainLength = int(BoardSetting[4])
   vmsParallel = int(BoardSetting[5])
   vmsbrightness = int(BoardSetting[6])
   # #Configuration for the matrix
   options = RGBMatrixOptions()
   options.rows = vmsRow
   options.chain_length =vmsChainLength
   options.parallel = vmsParallel
   options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
   options.gpio_slowdown = 2
   matrix = RGBMatrix(options = options)
   matrix.brightness = vmsbrightness	
   scheduler = BackgroundScheduler()
   scheduler.add_job(func=DoScheduleDisplay, trigger="interval", seconds=2)
   scheduler.start()

   # Shut down the scheduler when exiting the app
   atexit.register(lambda: scheduler.shutdown())
   app.run(host='0.0.0.0',port=5000)