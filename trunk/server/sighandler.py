#!/usr/bin/python
#coding=UTF-8
"""
xmgo prj, ver 0.0.2
sighandler.py: handle signal
Xie guohong
2013/9/18
"""
__author__    = "Dingo"
__copyright__ = "Copyright 2013, xmgo Project"
__credits__   = ["goxiti project"]
__license__   = "GPL"
__version__   = "0.0.2"
__maintainer__= "Dingo"
__email__     = "guohong.xie@gmail.com"


import sys, os, time, threading 
import signal
import pdb

sys_sig_table={
    signal.SIGABRT : u"由调用abort函数产生，进程非正常退出 ",
    signal.SIGFPE : u"数学相关的异常，如被0除，浮点溢出，等等 ",
    signal.SIGILL : u"非法指令异常 ",
    signal.SIGINT : u"由Interrupt Key产生，通常是CTRL+C或者DELETE。发送给所有ForeGround Group的进程 ",
    ##########signal.SIGKILL : u"无法处理和忽略。中止某个进程 ",
    signal.SIGSEGV : u"非法内存访问 ",
    #######signal.SIGSTOP : u"中止进程。无法处理和忽略。 ",
    signal.SIGTERM : u"请求中止进程，kill命令缺省发送 ",
}

def paishen_exit():
    print "[paishen websrv exit. time:%s]" % str(time.time())
    sys.exit()

def ps_sig_handler(sig, frame):
    global sys_sig_table
    print "got an signal", sig, frame
    sigs = sys_sig_table.keys()
    if  sig in sigs:
        ##print sys_sig_table[sig]
        if sig == signal.SIGKILL or signal.SIGSTOP:
            paishen_exit()
            return None

def init_signal_handler():
    global sys_sig_table
    sigs = sys_sig_table.keys()
    #pdb.set_trace()
    sigs.sort()
    for sig in sigs:
        ##print "sig=%d, %s" % (sig, sys_sig_table[sig])
        signal.signal(sig, ps_sig_handler)

if __name__ == '__main__':
    init_signal_handler()
    def sleep_main():
        TIME=10
        time.sleep(TIME)
        print 'normally exit'
    sleep_main()



