#!/usr/bin/env python
#coding=UTF-8
"""
xmgo prj, ver 0.0.2
xmgo-daemon.py: linux daemon module
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

import sys, time, os

def start_daemon():
    import public
    import websrv
    args = {}
    args['daemon'] = True
    args['conf'] = "conf/websrv.conf"
    args['webui'] = "../webui/" 
    args['logfile'] = os.path.abspath(public.LOG_FILE)
    websrv.start_websrv(**args)

def stop_daemon():
    pass

def restart_daemon():
    stop_daemon()
    start_daemon()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            start_daemon()
        elif 'stop' == sys.argv[1]:
            stop_daemon()
        elif 'restart' == sys.argv[1]:
            restart_daemon()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
