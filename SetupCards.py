#!/usr/bin/python3
##########################################################################################
####	Copyright 2014 (BSD License) Credits:  Florian Otto(Solider) and hadara
####					based on http://bsd.ee/~hadara/blog/?p=1017&cpage=1
####--------------------------------------------------------------------------------------
#### VCC- pin 1, 3.3 volts ||| RST- pin 22, GPIO25 ||| GND- pins, 6, 9, 14, 20, or 25,
####	MISO- pin 21, GPIO9 ||| MOSI- pin 19, GPIO10 ||| SCK- pin 23, GPIO11
####	NSS- pin 24, GPIO7 ||| IRQ- Don’t Attach to rpi
####--------------------------------------------------------------------------------------
####								remixed by plenkyman
##########################################################################################
####  			! ! THIS PROGRAM SETS UP THE CARDS, NOTHING TO MODIFY ! !
##########################################################################################
import TheDoorConfig as tdc
import shlex
import subprocess
import sys
import os
import time
import picamera
import datetime
import pymysql
import RPi.GPIO as GPIO
import _thread
### enter boot up in database
connection = pymysql.connect(host=tdc.rpi_ip,unix_socket='/var/run/mysqld/mysqld.sock', user=tdc.dbUs, passwd=tdc.dbPW, db=tdc.dbNa)
cursor = connection.cursor()
cursor.execute("""INSERT INTO """+(tdc.dbAc)+"""(id,acc,card,nam,err) VALUES ('0',NOW(),'python','pi01 at boot','program booted')""")
cursor.close()
connection.commit()
connection.close ()
### initial setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(tdc.green, GPIO.OUT) 
GPIO.setup(tdc.red, GPIO.OUT) 
GPIO.setup(tdc.yellow, GPIO.OUT) 
GPIO.setup(tdc.pstat,GPIO.OUT)
GPIO.setup(tdc.d_strike, GPIO.OUT)
GPIO.setup(tdc.d_unused, GPIO.OUT)
GPIO.setup(tdc.d_exit, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def powerstatus():
    tOn = 1
    tOff = .5
    exz = .99
    while 1:
        GPIO.output(tdc.pstat, True)
        time.sleep(tOn)
        GPIO.output(tdc.pstat, False)
        time.sleep(tOff)
        tOn = tOn * exz
        tOff = tOff * exz
        if tOn < .015:
           exz = 1.01
        elif tOn >= 1:
           exz = .99 

def blink(Color,bkg = 5):
    i=0
    while i <= bkg :
        GPIO.output(Color,1)
        time.sleep(.03)
        GPIO.output(Color,0)
        time.sleep(.03)
        i = i + 1
    else:
        GPIO.output(Color,0)
    ledsGRY(False,True,False)

def ledsGRY(st1,st2,st3):
    GPIO.output(tdc.green,st1)
    GPIO.output(tdc.red,st2)
    GPIO.output(tdc.yellow,st3)

def printto(wichlog,*args):
    for arg in args:
        print (arg),
    

def takepict(fn,err):
    if tdc.OnOffPiCam == "on":
        camera = picamera.PiCamera()
        camera.exposure_mode = tdc.picem
        camera.rotation = tdc.camrot
        time.sleep(.1)
        camera.capture(tdc.path_to_pics+time.strftime("%y-%m-%d_%H:%M:%S")+'_'+fn+'_'+err+'.'+tdc.camff)
        camera.close()
    else: return None

def scheduled_access(weekdays):
    if (str(datetime.datetime.today().weekday()) in weekdays) is True:
        thisHour = datetime.datetime.today().hour
        if datetime.datetime.today().weekday() <= 4 and thisHour >= hours_wk_st - 1 and thisHour <=hours_wk_end - 1:
            return True
        elif datetime.datetime.today().weekday() >= 5 and thisHour >= hours_wkend_st -1 and thisHour <=hours_wkend_end -1:
            return True
        else:
            return False
    else:
        return False

def opendoor():
    GPIO.remove_event_detect(tdc.d_exit)
    GPIO.output(tdc.d_strike,0)
    time.sleep(tdc.d_time)
    GPIO.output(tdc.d_strike,1)
    GPIO.add_event_detect(tdc.d_exit, GPIO.FALLING, callback = exitbutton_callback, bouncetime = (tdc.d_time * 1000) + 500)

def exitbutton_callback(channel) :
    GPIO.output(tdc.d_strike,0)
    if OverRide == "A":
        ledsGRY(False,False,False)
        _thread.start_new_thread(blink, (tdc.green,42))
        printto(tdc.logf,time.strftime("%c")+ " : Exit Button")
        time.sleep(tdc.d_time)
        GPIO.output(tdc.d_strike,1)
        ledsGRY(False,True,False)
    else:
        printto(tdc.logf,time.strftime("%c") + " : Exit Button, Door on OverRide")
############# READING CARDS RC522 #############################
class RFIDReaderWrapper(object):
    _thread.start_new_thread(powerstatus, ())
    """runs rfid reader as a subprocess & parses tag serials
    from its output
    """
    def __init__(self, cmd):
        self._cmd_list = shlex.split(cmd)
        self._subprocess = None
        self._init_subprocess()

    def _init_subprocess(self):
        self._subprocess = subprocess.Popen(self._cmd_list,
            stderr=subprocess.PIPE)

    def read_tag_serial(self):
        """blocks until new tag is read
        returns serial of the tag once the read happens
        """
        if not self._subprocess:
            self._init_subprocess()

        while 1:
            line = self._subprocess.stderr.readline()
            if isinstance(line, bytes):
                # python3 compat
                line = line.decode("utf-8")

            if line == '':
                # EOF
                return None

            if not line.startswith("New tag"):
                continue

            serial = line.split()[-1].split("=", 1)[1]
            return serial
####### SET STATE TO BEGIN  #############
OverRide = "A"
GPIO.setwarnings(True)  
GPIO.output(tdc.d_strike,1)
GPIO.output(tdc.d_unused,0)
ledsGRY(False,True,False)
printto(tdc.logpi,time.strftime("%H:%M:%S-%m-%d-%y")+" : ### Swipe a new card or cancel with control c ###")                        
####### RUNNING THE READER  #############
try:
    if __name__ == '__main__':
        reader = RFIDReaderWrapper("sudo nohup "+tdc.p2r+"/rc522_reader -d 2>&1")
        name=""
        GPIO.add_event_detect(tdc.d_exit, GPIO.FALLING, callback = exitbutton_callback, bouncetime = (tdc.d_time * 1000) + 500)
        while True:
            connection = pymysql.connect(host=tdc.rpi_ip,unix_socket='/var/run/mysqld/mysqld.sock', user=tdc.dbUs, passwd=tdc.dbPW, db=tdc.dbNa)
            cursor = connection.cursor()
            serial = reader.read_tag_serial()
            cursor.execute("""SELECT name,acc_group,counter,access,weekdays,hours_wk_st,hours_wk_end,hours_wkend_st,hours_wkend_end FROM """+(tdc.dbKe)+""" WHERE ID=(%s)""", (serial))
            for row in cursor.fetchall():
                name = str(row[0])
                acc_group = str(row[1])
                counter = int(row[2])
                access = int(row[3])
                weekdays = str(row[4])
                hours_wk_st = int(row[5])
                hours_wk_end = int(row[6])
                hours_wkend_st = int(row[7])
                hours_wkend_end = int(row[8])

            if name=="":
                print (" Choose wich card you would like to authorize or or cancel with control c: ")
                print (" 1: Make House Card")
                print (" 2: Make Guest Card")
                print (" 3: Make OverRide Card")
                print (" 4: Make your # 1 House card")
                print (" 5: cancel request, exit program")
                wichcard = int(input("Choose 1 - 4: "))
                if wichcard == 1:  
                    print (serial+" ,is now registerd as MakeHouse card.")
                    print ("Swipe a new card or quit program: control c")
                    cursor.execute("""UPDATE """+(tdc.dbKe)+""" SET ID = (%s) WHERE OrderID = 1""",(serial));
                elif wichcard == 2: 
                    print (serial+" ,is now registerd as MakeGuest card.")
                    print ("Swipe a new card or quit program: control c")
                    cursor.execute("""UPDATE """+(tdc.dbKe)+""" SET ID = (%s) WHERE OrderID = 2""",(serial));
                elif wichcard == 3:
                    print (serial+" ,is now registerd as OverRide card.")
                    print ("Swipe a new card or quit program: control c")
                    cursor.execute("""UPDATE """+(tdc.dbKe)+""" SET ID = (%s) WHERE OrderID = 3""",(serial));
                elif wichcard == 4:
                    yourname=input("type your first and given name :")  
                    print (yourname+" ,your card :"+serial+",is registerd now.")
                    print ("Swipe a new card or quit program: control c")
                    cursor.execute("""UPDATE """+(tdc.dbKe)+""" SET ID = (%s),name = (%s) WHERE OrderID = 4""",(serial,yourname));
                elif wichcard == 5:
                    print ("request cancelled")
                    os.system(tdc.pathtoscript + "restartdoor")
                else:
                    print ("No valid selection")
                    print ("Swipe a new card or or cancel with control c")
### unknown cards
            else: 
               print ("This card is already registerd !")
               print ("Swipe a new card or or cancel with control c")
            cursor.close()
            connection.commit()
            connection.close ()
            name=""

except BaseException as error:
    ledsGRY(False,False,False)
    GPIO.output(tdc.pstat, False)
    GPIO.cleanup()
    cursor.close()
    connection.commit()
    connection.close ()
finally:    
    sys.exit(0)    
