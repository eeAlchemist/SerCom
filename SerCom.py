#-------------------------------------------------------------------------------
# Name: SerCom.py
# Purpose: A class that is used to parse data from the serial port and fill
#           a FIFO buffer with data. Date is distributed by calling the next()
#           method
#
# Author: eeAlchemist - http://eealchemy.wordpress.com
#
# Created: 15SEP11
#
# Licence: This work is licensed under a
#          Creative Commons Attribution-ShareAlike 3.0 Unported License.

# Based on the works of:
#http://www.blendedtechnologies.com/realtime-plot-of-arduino-serial-data-using-python/231
#           https://github.com/gregpinero/ArduinoPlot
#
# ToDo: More error trapping
# ToDo: More commenting
# ToDo: configure serial port with data pass to init
# ToDo: create a send() method
# ToDo:
# ToDo:
#-------------------------------------------------------------------------------
#!/usr/bin/env python


import matplotlib.pyplot as plt
from threading import Thread
import time
import serial
import datetime
import xyData


class SerCom(object):
    '''sets up the serial port and if connected starts a thread to poll
    the serial port by calling the receiving method. Any data recieved is
    added to a buffer where it is checked for a \n. A \n sets the end of valid
    data. Commands and data are appended to a received list where the are popped off
    in a FIFO order. This makes a double buffer and hopefully none will
    be lost '''
    def __init__(self, init=50):
        self.recvRate=0.2
        self.received =[]

        try:
            self.ser = serial.Serial(
                port='com3',
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
                xonxoff=0,
                rtscts=0,
                interCharTimeout=None
            )
        except serial.serialutil.SerialException:
            #no serial connection
            print 'Serial connection NOT found.'
            self.ser = None
        else:
            self.done=False
            print 'Serial connection found.'
            comEngine = Thread(target=self.receiving, args=(self.ser,))
            comEngine.start()

    def next(self):
        '''Processes the next recieved command '''
        if not self.ser:
            XX = datetime.datetime.now()
            tmpStr = str(XX.second)+','+str(XX.second)
            return tmpStr
        #return anything so we can test when Arduino isn't connected
        #return a  value or try a few times until we get one
        for i in range(40):
            if len(self.received) > 0:
                return self.received.pop(0)
            else: time.sleep(self.recvRate/4)


    def __del__(self):
        if self.ser:
            self.ser.close()
            self.done=True

    def receiving(self, ser):
        buffer = ''
        while not self.done:
            buffer = buffer + ser.read(ser.inWaiting())
            if '\n' in buffer:
                lines = buffer.split('\n') # Guaranteed to have at least 2 entries
                self.received.append(lines[-2])# double buffered using a list
                buffer = lines[-1]
            time.sleep(self.recvRate/4.0)
        return False


if __name__=='__main__':
   s = SerCom()
   for i in range(10):
       print s.next()

