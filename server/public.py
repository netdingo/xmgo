#coding=UTF-8
"""
xmgo prj, ver 0.0.2
Xie guohong
2013/09/18
"""
import os, sys, time, struct, threading, thread, platform

HOME      = "."
CONF_DIR  = "conf"
LOG_DIR   = "log"
WEBUI_DIR = "webui"
XITI_DIR  = "sgf"
XITIDB_DIR= "db"
WEBUI_HOME= os.path.abspath(os.path.join("..", WEBUI_DIR))
XITI_HOME = os.path.abspath(os.path.join("..", XITI_DIR))

CONF_FILE = "websrv.conf"

CONF_HOME = os.path.abspath(os.path.join(HOME, CONF_DIR))
LOG_HOME  = os.path.abspath(os.path.join(HOME, LOG_DIR))
XITI_DB_HOME= os.path.abspath(os.path.join(CONF_HOME, XITIDB_DIR))
if not os.path.exists(XITI_DB_HOME):
    import FileUtility as fu
    fu.createDir(XITI_DB_HOME)

SRV_CONF  = os.path.join(CONF_HOME, CONF_FILE)
DB_FILE   = os.path.abspath(os.path.join(LOG_HOME, "mbdb.dat"))
LOG_FILE  = os.path.abspath(os.path.join(LOG_HOME, "log.txt"))
INDEX_PAGE= os.path.abspath(os.path.join(WEBUI_HOME, "weiqi.htm"))
XITI_CONF = os.path.abspath(os.path.join(CONF_HOME, "xiti.conf"))
SGF_DB    = os.path.abspath(os.path.join(XITI_HOME, "sgf.db")) ## sgf tar

SGF_DB_FILE = 0
SGF_DB_TAR  = 1
SGF_DB_SQL  = 2

bool_tbl  = {'True': True, 'False': False}

def get_websrv_conf():
    webconf = None
    if platform.system() == 'Windows':
        webconf = os.path.join(os.path.dirname(sys.path[0] + os.path.sep ), SRV_CONF)
    else:
        dirlist = [ "./", CONF_HOME , "/etc/" ]
        for dir in dirlist:
            webconf = os.path.join(dir, CONF_FILE)
            webconf = os.path.abspath(webconf)
    if os.path.exists(webconf): ## 如果配置文件存在于指定目录
        return os.path.abspath(webconf)
    else:
        return None

def get_webui_path():
    path = None
    cd = os.getcwd()
    dirlist = [ os.path.join(cd, WEBUI_DIR), WEBUI_HOME ]
    for dir in dirlist:
        path = os.path.abspath(dir)
        break
    if os.path.exists(path):
        return path 
    else:
        return None

get_arg = lambda k, args, v: args[k] if k in args and args[k] != None else v
