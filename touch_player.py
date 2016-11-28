"""
   player .py

   :description: Plays back MQTT message record 

   :author: Vikram Pawar
   :copyright: Whirlpool Corporation

"""
import sys
import imp
import os.path
from time import sleep
import argparse

class FileManager:
    def __init__(self,fname):
        if(os.path.isfile(fname)):
            self._f = open(fname,'ab+')
        else:
            self._f = open(fname,'wb+')

    def ReadAll(self):
        return self._f.read()

    def ReadLine(self):
        return self._f.readline()

    def Rewind(self):
        return self._f.seek(0)

    def Position(self):
        return self._f.tell()

    def Write(self,data):
        self._f.write(data)
        self._f.flush()

    def WriteLine(self,line):
        return self._f.write(line+'\n')

    def End(self):
        return self._f.close()


class Touch_Player:
    def __init__(self,fname,callback):
        self._fm = FileManager(fname)
        self._cb = callback
        self._started = False

    def Start(self):
        self._started = True
        while self._started:
            data = self._fm.ReadAll()
            if data == None or data == "":
                self.Stop()
                return
            lines = data.split("@##@##@##@##");
            for line in lines:
                if len(line) > 0:
                    delay,data = line.split("@#@#@#")
                    delay = float(delay)
                    sleep(delay)
                    #sleep(0.1001)
                    self._cb(data)

    def Stop(self):
        self._started = False
        self._fm.End()

def cb(payload):
    global O
    #print payload
    os.stdout.write(payload)
    O.write(payload)
    O.flush()


def main(argv):
    parser = argparse.ArgumentParser(description='Plays back touch events')
    parser.add_argument('-i','--input',default="touch.record",help="Path to touch record input file")
    parser.add_argument('-o','--output',default="/dev/virtual_touchscreen",help="Path to output device")
    args = parser.parse_args()

    global O

    O = open(args.output,"w")
    p = Touch_Player(args.input,cb)
    p.Start()


if __name__ == "__main__":
    main(sys.argv[1:])
