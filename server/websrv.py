#coding=UTF-8
"""
xmgo prj, ver 0.0.2
websrv.py: starting module
Xie guohong
2013/09/18
"""
__author__    = "Dingo"
__copyright__ = "Copyright 2013, xmgo Project"
__credits__   = ["goxiti project"]
__license__   = "GPL"
__version__   = "0.0.2"
__maintainer__= "Dingo"
__email__     = "guohong.xie@gmail.com"


import sys, os
#the following cherry import statement is used to fix

try:
    import cherrypy._cptools
    import cherrypy._cprequest
    import cherrypy._cpconfig
    import cherrypy._cplogging
except Exception, e:
    pass

try:
    import cherrypy.process.plugins
    import cherrypy.process.servers
except Exception, e:
    pass

try:
    import cherrypy._cpserver
    import cherrypy._cpchecker
    import cherrypy.lib.cptools
    import cherrypy.lib.encoding
    import cherrypy.lib.auth
    import cherrypy.lib.static
    import cherrypy.lib.tidy
    from   cherrypy.lib.static import serve_file
    from   cherrypy.lib.static import staticfile
    from   cherrypy.lib.static import serve_download
    from cherrypy.process.plugins import Daemonizer
except Exception, e:
    pass

try:
    import cherrypy._cpcgifs
    import cherrypy.wsgiserver
except Exception, e:
    pass
#--------------------------------------------------

#from mimetypes import guess_type
import cherrypy
import cgi, tempfile, getopt
import threading
import platform
import httpret
import sighandler
import public, controller, FileUtility
import xiti
import pdb

MB_ONLINE_DEBUG = False 
local_data = threading.local()
cherrypy_ver_maj = 0
cherrypy_ver_min = 0

def engine_exit_notify():
    getCmdAdmin().shutdown()

def getCmdAdmin():
    admin = controller.CommandController.admin
    if admin == None:
        admin = controller.CommandController()
    return admin

def noBodyProcess():
    cherrypy.request.process_request_body = False

def initUploadMode(socket_timeout = 60):
    cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)
    # remove any limit on the request body size; cherrypy's default is 100MB
    # (maybe we should just increase it ?)
    cherrypy.server.max_request_body_size = 0
    # increase server socket timeout to 60s; we are more tolerant of bad
    # quality client-server connections (cherrypy's defult is 10s)
    cherrypy.server.socket_timeout = socket_timeout

initUploadMode()

class TimerThread(threading.Thread):
    """Thread that executes a task every N seconds"""
    def __init__(self, interval = 10.0):
        threading.Thread.__init__(self)
        self._finished = threading.Event()
        self._interval = interval
    
    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
    
    def shutdown(self):
        """Stop this thread"""
        self._finished.set()

    def sleep(self):        
        self._finished.wait(self._interval)
    
    def run(self):
        while True:
            if self._finished.isSet(): break 
            self.handler()
            # sleep for interval or until shutdown
            self.sleep()
        print "exit TimerThread!"
    
    def handler(self):
        """The task done by this thread - override in subclasses"""
        assert(0)
        pass


class AppPage:
    _cp_config  = {'tools.sessions.on': True}
    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        # Every yield line adds one part to the total result body.
        home_page = public.INDEX_PAGE
        if not FileUtility.fileExists(home_page):
                yield "您所访问的页面不存在！"
        if FileUtility.fileSize(home_page) <= 1024:
            content = FileUtility.fileRead( home_page ) 
            if content == None: 
                content = "您所访问的页面不存在！"
            yield content
        else:
            try:
                fp = None
                fp = open(home_page, "rb")
                max_size = FileUtility.fileSize(home_page)
                pos = 0 
                size = 1024
                while pos < max_size: 
                    if pos + size >= max_size:
                        size = max_size - pos
                    content = fp.read(size)
                    yield content
                    pos += size
            except Exception, e:
                pass
            finally:
                if fp: fp.close()
                pass
    index.exposed = True

    def error_page_404(status, message, traceback, version):
        return "您所访问的页面不存在！"
    cherrypy.config.update({'error_page.404': error_page_404})

    @cherrypy.expose
    def priv(self, **args):
        """
            只能从localhost发起：
        """
        remoteip = cherrypy.request.remote.ip 
        cmds = ['state', 'shutdown', 'update_arrival']
        if not args.has_key('cmd'): return ""
        cmd = args['cmd'].lower()
        if cmd not in cmds: return ""
        if cmd == 'shutdown' and remoteip == '127.0.0.1':
            stop_websrv()
        if cmd == 'state' and remoteip == '127.0.0.1':
            return '1'
        if cmd == 'update_arrival' and remoteip == '127.0.0.1':
            if args.has_key('ver'):
                version =  u"(%s)" % args['ver']
            else:
                version =  u""
            import psupdater
            psupdater.setupUpdatingNews(version)
            return '1'
        return ""

    @cherrypy.expose
    def get_current_sgf(self, **args):
        admin = getCmdAdmin()
        xiti = admin.get_item('xiti')
        if xiti: 
            return xiti.load_sgf()
        else:
            return ""

    @cherrypy.expose
    def xmgo(self, item, cmd, **args):
        global MB_ONLINE_DEBUG, local_data
        if MB_ONLINE_DEBUG: pdb.set_trace() 
        args['remoteip'] = cherrypy.request.remote.ip 
        local_data.remoteip = cherrypy.request.remote.ip 
        retval = getCmdAdmin().dispatch(item, cmd, args) 
        if retval == None :
            return self.returnHttpResponse('ajax', success=False, event=cmd, info=u"error when handling cmd[%s]"%cmd)
        else:
            logret = True
            if item == 'xiti':
                logret = False
                if cmd == 'load_sgf':  ## 下载命令不进行UTF-8编码
                    return retval
            return self.returnHttpResponse('httpret', obj=retval, logret=logret)  ## 返回对象类型

    def getArg(self, kargs, key, defval):
        if kargs.has_key(key):
            return kargs[key]
        else:
            return defval

    def returnHttpResponse(self, retType, **kargs):
        """
           先统一将各种类型转换为httpret.httpRetRecord类型，然后调用getmsg来转换
           最终返回的字符串。
           参数：
               'obj'    : 可能是httpret.httpRetRecord对象，也可能是python对象
               'success': extjs要求的返回值，一般是'ajax'返回类型的强制参数
               'event'  : 可选参数
               'info'   : 当retType是'ajax'时，其一般是extjs要求的返回信息，此时
                          其为强制，如果retType是'str'时，其表示直接返回的字符串。
        """
        cherrypy.response.headers['Content-Type']='text/xml'
        cherrypy.response.headers['charset']='charset=utf-8'
        obj = self.getArg(kargs, 'obj', None)
        logret = self.getArg(kargs, 'logret', True)
        ##success=success, event=event, info=info
        if retType == 'httpret' :
            if obj and not isinstance(obj, httpret.httpRetRecord):
                obj = httpret.createHttpReturn('ajax', **kargs)
        else:
            obj = httpret.createHttpReturn(retType, **kargs)
        if not obj:
            msg = ""
        elif isinstance(obj, httpret.psManualReturn):   ## 如果是手册，则直接返回。
            return obj.getmsg()
        else:
            msg = obj.getmsg()
        ## LOG记录每个HTTP响应
        ##print "   ---> HttpResp : %s" % msg
        return msg

def print_help():
    print "usage: "
    print "websrv [-d] -c conf_file -w webui_dir" 
    print "    -d:        run as daemon"
    print "    conf_file: websrv config file"
    print "    webui_dir: websrv static web page home"
    sys.exit(-1)

def get_cherrypy_conf(**kargs):
    webconf = public.get_arg('conf', kargs, public.SRV_CONF) 
    ## 如果参数带有配置文件，检查其存不存在
    if not os.path.exists(webconf):
        ## 如果参数不带配置文件，或配置文件不存在则检查当前目录是否存在配置文件
        webconf = public.get_websrv_conf()
    if not webconf or not os.path.exists(webconf):
        print_help()
    else:
        return os.path.abspath(webconf)

def get_static_page_dir(**kargs):
    path = public.get_arg('webui', kargs, public.WEBUI_HOME)
    if not os.path.exists(path):
        path = public.get_webui_path()
    if not path or not os.path.exists(path):
        print_help()
    else:
        return os.path.abspath(path)

def mount_static_page(static_page_dir, **kargs ):
    conf={
        '/':{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':static_page_dir,
            'tools.patch_set_cookie.on':True
        }
    }
    run_as_daemon = public.get_arg('daemon', kargs, False)
    if run_as_daemon:
        logfile = public.get_arg('logfile', kargs, None)
        if logfile:
            daemon_eng = Daemonizer(cherrypy.engine, stdout=logfile, stderr=logfile)
        else:
            daemon_eng = Daemonizer(cherrypy.engine)
        daemon_eng.subscribe()
    if cherrypy_ver_maj < 3:
        cherrypy.tree.mount(AppPage(), conf=conf)
    else:
        cherrypy.tree.mount(AppPage(), config=conf)

mbwebsrv_stoped = False
def stop_websrv():
    global mbwebsrv_stoped
    getCmdAdmin().shutdown()
    mbwebsrv_stoped = True
    cherrypy.engine.exit()
    print "begin to stop_websrv:"
    class websrvTerminator(TimerThread):
        def __init__(self, interval):
            TimerThread.__init__(self, interval)
        def run(self):
                self.sleep()
                os._exit(0)
    websrvTerminator(3).start() ## 延迟2秒退出的原因是，让这个shutdown请求能够正确返回

def isWebsrvStoped():
    global mbwebsrv_stoped
    return mbwebsrv_stoped

def getCherrypyVersion():
    global cherrypy_ver_maj, cherrypy_ver_min
    try:
        ver = cherrypy.__version__
        ver = ver.split(".")
        cherrypy_ver_maj = int(ver[0])
        cherrypy_ver_min = int(ver[1])
    except:
        cherrypy_ver_maj = 0
        cherrypy_ver_min = 0

def patch_set_cookie():
    """
        原来的Set-Cookie值象下面这样：
           Set-Cookie:session_id=3984e51123bb883a51bcb47b48ad42706ebcf849; expires=Sat, 27 Mar 2010 07:05:03 GMT; Path=/
        删掉 expires 项，因为如果有这项的话，当服务器时间不正确时，IE 或 chrome将不会把session_id传给服务器。
    """
    setCookie = None 
    if cherrypy.response.header_list:
        for kv in cherrypy.response.header_list:
            name, value = kv
            if name == 'Set-Cookie':
                setCookie = value 
                break
    if setCookie == None: return
    del_val = None
    vl = setCookie.split(";")
    for v in vl:
        exp_v = v
        v = v.strip().lower()
        if v.startswith('expires'): 
           del_val = v
           break
    if del_val: 
        vl.remove(exp_v)
        setCookie = ";".join(vl)
        cherrypy.response.header_list.remove(kv)
        cherrypy.response.header_list.append(('Set-Cookie', setCookie))

cherrypy.tools.patch_set_cookie=cherrypy.Tool('on_end_resource', patch_set_cookie)

def pageDoesNotExist( status, message, traceback, version):
    # do something here
    raise cherrypy.HTTPRedirect("/about.html")
    pass

def setLocale():
    """
     COUNTRY="cn"
     LANG="zh_CN.UTF-8"
     KEYTABLE="us"
     XKEYBOARD="us"
     KDEKEYBOARD="us"
     CHARSET="utf8"
     KDEKEYBOARDS="us,de(nodeadkeys),fr"
     XMODIFIERS="@im=Chinput"
     TZ="Asia/Shanghai" 
    """
    import locale
    #zh_locale = 'zh_CN.UTF-8'
    zh_locale = 'en_US.UTF-8'
    try:
        locale.setlocale(locale.LC_ALL, zh_locale)
    except:
        pass
    pass

def start_websrv(**kargs):
    setLocale()
    getCherrypyVersion()
    webconf = get_cherrypy_conf(**kargs) 
    static_page_dir = get_static_page_dir(**kargs) 
    mount_static_page(static_page_dir, **kargs)
    #cherrypy.config.update({'error_page.404': pageDoesNotExist })
    if platform.system() == 'Windows':
        ###cherrypy.engine.start(config=webconf)
        cherrypy.quickstart(config=webconf)
    else: ## linux
        if cherrypy_ver_maj == 3:
            cherrypy.config.update(webconf)
            ## quickstart语句可以保证当源码有改动时，cherrypy会重新启动。
            cherrypy.server.quickstart()
            cherrypy.engine.start()
        else:
            cherrypy.server.start(config=webconf)
    ## 设置信号处理
    sighandler.init_signal_handler()

    ## 加入如行的原因是：如果没下行，freeze.py打包后的可执行文件会直接退出。
    cherrypy.engine.block()

def create_opt_dict(short_opt, long_opt):    
    s = map(lambda x : x, short_opt.replace(":", ""))
    l = map(lambda x : x.rstrip("="), long_opt)
    kargs = {}
    i = 0
    for x in s:
        kargs["-" + x] = l[i]
        i += 1
    for x in l:
        kargs["--" + x] = x
    return kargs

def handle_opt(argv):    
    argc = len(argv)
    ## short 和 long 选项必须一一对应
    short_opt = "hdc:w:"
    long_opt  = ["help", "daemon", "conf=", "webui="] 
    opt_dict = create_opt_dict(short_opt, long_opt)
    try:
        opts, remaining = getopt.getopt(argv, short_opt, long_opt)
    except getopt.GetoptError: 
        print_help()
    kargs = {}
    for opt, value in opts:
        if opt in opt_dict:
            if value == "": value = True
            kargs[opt_dict[opt]] = value
    start_websrv(**kargs)

if __name__ == '__main__':
    handle_opt(sys.argv[1:])

