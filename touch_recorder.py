#!/usr/bin/python

import sys
import os
import struct
import argparse

class FileManager:
    def __init__(self,fname):
        if(os.path.isfile(fname)):
            self._f = open(fname,'ab+')
        else:
            self._f = open(fname,'wb+')

    def Read(self,length):
        return self._f.read(length)

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



def decode_ev_type(evt):
    '''
    get the event type string
    '''
    if evt == 0x00:
        evts = 'EV_SYN'
    elif evt == 0x01:
        evts = 'EV_KEY'
    elif evt == 0x02:
        evts = 'EV_REL'
    elif evt == 0x03:
        evts = 'EV_ABS'
    elif evt == 0x04:
        evts = 'EV_MSC'
    elif evt == 0x05:
        evts = 'EV_SW'
    elif evt == 0x11:
        evts = 'EV_LED'
    elif evt == 0x12:
        evts = 'EV_SND'
    elif evt == 0x14:
        evts = 'EV_REP'
    elif evt == 0x15:
        evts = 'EV_FF'
    elif evt == 0x16:
        evts = 'EV_PWR'
    elif evt == 0x17:
        evts = 'EV_FF_STATUS'
    elif evt == 0x1f:
        evts = 'EV_MAX'
    elif evt == 0x20:
        evts = 'EV_CNT'
    else:
        evts = 'UNKNOWN EV TYPE (%d)' % evt
    return evts


def decode_ev_key_code(code):
    '''
    get the event key code string
    '''
    if code == 0x14a:
        cs = 'BTN_TOUCH'
    else:
        cs = 'UNKNOWN KEY CODE (%s)' % code
    return cs


def decode_ev_abs_code(code):
    '''
    get the event abs code string
    '''
    if code == 0x00:
        cs = 'ABS_X'
    elif code == 0x01:
        cs = 'ABS_Y'
    elif code == 0x02:
        cs = 'ABS_Z'
    elif code == 0x18:
        cs = 'ABS_PRESSURE'
    elif code == 0x19:
        cs = 'ABS_DISTANCE'
    elif code == 0x1c:
        cs = 'ABS_TOOL_WIDTH'
    elif code == 0x20:
        cs = 'ABS_VOLUME'
    elif code == 0x28:
        cs = 'ABS_MISC'
    elif code == 0x30:
        cs = 'ABS_MT_TOUCH_MAJOR'
    elif code == 0x31:
        cs = 'ABS_MT_TOUCH_MINOR'
    elif code == 0x32:
        cs = 'ABS_MT_WIDTH_MAJOR'
    elif code == 0x33:
        cs = 'ABS_MT_WIDTH_MINOR'
    elif code == 0x34:
        cs = 'ABS_MT_ORIENTATION'
    elif code == 0x35:
        cs = 'ABS_MT_POSITION_X'
    elif code == 0x36:
        cs = 'ABS_MT_POSITION_Y'
    elif code == 0x37:
        cs = 'ABS_MT_TOOL_TYPE'
    elif code == 0x38:
        cs = 'ABS_MT_BLOB_ID'
    elif code == 0x39:
        cs = 'ABS_MT_TRACKING_ID'
    elif code == 0x3a:
        cs = 'ABS_MT_PRESSURE'
    elif code == 0x3f:
        cs = 'ABS_MAX'
    elif code == 0x40:
        cs = 'ABS_CNT'
    else:
        cs = 'UNKNOWN ABS CODE (%s)' % code
    return cs


def decode_ev_syn_code(code):
    '''
    get the event syn code string
    '''
    if code == 0x00:
        cs = 'SYN_REPORT'
    elif code == 0x01:
        cs = 'SYN_CONFIG'
    elif code == 0x02:
        cs = 'SYN_MT_REPORT'
    else:
        cs = 'UNKNOWN SYN CODE (%d)' % code
    return cs


def decode_event_line(line):
    '''
    Decode the line with event data
    '''
    event_type = line[21:24]
    evt = decode_ev_type(event_type)

    event_code = line[25:29]
    if evt == 'EV_ABS':
        evc = decode_ev_abs_code(event_code)
    elif evt == 'EV_KEY':
        evc = decode_ev_key_code(event_code)
    elif evt == 'EV_SYN':
        evc = decode_ev_syn_code(event_code)
    else:
        evc = 'UNKNOWN EV TYPE CODE (%d)' % evt

    event_value = line[30:38]
    if evc == 'SYN_REPORT':
        evv = str(int(event_value, 16)) + '\n\n'
    else:
        evv = str(int(event_value, 16)) + '\n'

    res = evt + ' ' + evc + ' ' + evv
    return res


def print_output(x,delay):
    global record
    global O

    if record:
        #sys.stdout.write("{0}@#@#@#{1}@##@##@##@##".format(delay,x))
        #sys.stdout.flush()
        O.Write("{0}@#@#@#{1}@##@##@##@##".format(delay,x))

    else:
        print x


def print_evt(data):
    global need_mouseemu,relx,rely,delay,last_time

    (sec,usec,ev_type,code,val) = struct.unpack("LLhhl",data)


    time = float("{}.{}".format(sec,usec))
    if last_time == 0:
        last_time = time
    delay = time - last_time
    if delay < 0: delay = 0.0
    last_time = time 

    if ev_type == 1:
        if val == 1:
            #print_output( "d 0", delay)
            print_output( "d 0\nS 0\n", delay)
        else:
            #print_output( "u 0", delay)
            print_output( "u 0\nS 0\n", delay)

    if ev_type == 2:
        # relative positioning
        if code == 0:
            relx += val 
        elif code == 1:
            rely += val 

        print_output( "x {0}\ny {1}\nS 0\n".format(relx,rely), delay)
   
    if ev_type is not 3:
        if need_mouseemu:
            need_mouseemu = 0
            print_output( "e 0\nS 0\n",delay)

    if code == 0x2f:
        print_output( "s {}\n".format(val),delay)
    elif code == 0x39:
        #print_output( "T {}\nS 0\n".format(val),delay)
        print_output( "T {}\n".format(val),delay)
    elif code == 0x35:
        print_output( "X {}\n".format(val),delay)
        need_mouseemu=1
    elif code == 0x36:
        print_output( "Y {}\n".format(val),delay)
        need_mouseemu=1

    # my SE Xperia X10 driver sends this
    if code == 0x30 and not val:
        print_output( "a 0\ne 0\nS 0\n",delay)
        need_mouseemu=0

    elif code == 0x30 and val:
        print_output( "a 1\ne 0\nS 0\n",delay)
        need_mouseemu=0 

def parse_evt(data):
    global cur_state,cur_x,cur_y,cur_time,next_state,next_x,next_y,start_time

    (sec,usec,ev_type,code,val) = struct.unpack("LLhhl",data)

    ev_type = decode_ev_type(ev_type)
    if ev_type == 'EV_ABS':
        code = decode_ev_abs_code(code)
        if code == 'ABS_X':
            next_x = val
        elif code == 'ABS_Y':
            next_y = val
    elif ev_type == 'EV_KEY':
        code = decode_ev_key_code(code)
        if code == 'BTN_TOUCH':
            if val == 1:
                next_state = "TOUCH"
            else:
                next_state = "NONE"
    elif ev_type == 'EV_SYN':
        code = decode_ev_syn_code(code)
    else:
        code = 'UNKNOWN EV TYPE CODE (%d)' % code
    
    if next_x != cur_x:
        cur_x = next_x
    if next_y != cur_y:
        cur_y = next_y
    if next_state != cur_state:
        cur_state = next_state
        start_time = float("{}.{}".format(sec,usec))  
        cur_time = 0.0
    else:
        cur_time = float("{}.{}".format(sec,usec)) - start_time

    print "time= {} {}".format(sec,usec)
    print "type={0}".format(ev_type)
    print "code={0}".format(code)
    print "val={0}".format(val)
    print "state=",cur_state
    print "x,y=",cur_x,cur_y
    print "time=",cur_time
    print "------------------"




def main():

    parser = argparse.ArgumentParser(description='Record touch events')
    parser.add_argument('-d','--device',default="/dev/input/event7",help="Path to touch input device")
    parser.add_argument('-o','--output',default="touch.record",help="Path to touch record output file")
    args = parser.parse_args()

    global D,O

    D = FileManager(args.device)
    O = FileManager(args.output)

    global record

    record = 1

    global need_mouseemu,relx,rely,delay,last_time

    need_mouseemu,relx,rely,delay,last_time = 0,0,0,0.0,0.0

    global cur_state,cur_x,cur_y,cur_time,next_state,next_x,next_y,start_time

    next_state,cur_state = "NONE","NONE"
    next_x,cur_x = -1,-1
    next_y,cur_y = -1,-1
    start_time = 0
    cur_time = 0

    while 1:
        #data =  sys.stdin.read(16)
        data =  D.Read(16)
        #print " ".join([ hex(ord(d)) for d in data ])
        parse_evt(data)
        print_evt(data)

if __name__ == '__main__':
    main()


