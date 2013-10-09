#coding=UTF-8
"""
xmgo prj, ver 0.0.2
misc.py: global misc function
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


import os, sys, time
import UnicodeUtil

ISOTIMEFORMAT='%Y-%m-%d %X'
LOCAL_TIMEFORMAT=u'%Y年%m月%d日 %X'
CHINA_TIMEFORMAT=u'%Y年%m月%d日 %H时%M分%S秒'
SIMPLE_TIMEFORMAT=u''

def time2str(t):
    tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = time.localtime(t)
    #return u'%04d年%02d月%02d日 %02d时%02d分%02d秒'%(tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec)
    return u'%04d年%02d月%02d日 %02d:%02d:%02d'%(tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec)

def str2time(ts):
    """
       将 ISOTIMEFORMAT, LOCAL_TIMEFORMAT 两种时间格式的字符串转换为秒数。
    """
    ts = UnicodeUtil.get_unicode_str(ts)
    global ISOTIMEFORMAT, LOCAL_TIMEFORMAT 
    for fmt in [ ISOTIMEFORMAT, CHINA_TIMEFORMAT, LOCAL_TIMEFORMAT ]:
        try:
            time_struct = time.strptime(ts, fmt)
            return int(time.mktime(time_struct))
        except Exception, e:
            continue
    return 0

def getTimeStr(ft = None, timeformat = ISOTIMEFORMAT):
    """
       将浮点数的时间转换为字符串时间。如果不提供参数，则转换当前时间。
    """
    if ft == None:
        ft = time.time()
    ts = time.strftime( timeformat, time.localtime( ft ) )
    return UnicodeUtil.get_unicode_str(ts)

def getLocalTime():
    return getTimeStr()

def getGMTTime():
    return UnicodeUtil.get_unicode_str( time.strftime( ISOTIMEFORMAT, time.gmtime( time.time() ) ))

def getArg(kargs, key, defval):
    if kargs.has_key(key):
        return kargs[key]
    else:
        return defval

def getHTMLHighlightText(txt, **kargs):
    v = {'highlight': 'h1',
         'fontsize':  '16',
         'fontcolor': 'blue',
        } 
    for key in v.keys():
        v[key] = getArg(kargs, key, v[key]) 
    v['txt'] = txt
    return u"<%(highlight)s style=\" font-size: %(fontsize)spx; color: %(fontcolor)s\">%(txt)s</%(highlight)s>" % v

def encodeURL(baseUrl, paramDict):
    if baseUrl:
        url = baseUrl
        import urllib, UnicodeUtil
        if isinstance(baseUrl, unicode):
            url = baseUrl.encode('ascii')
        url = url.rstrip("/")
        if '?' in url:
            url += '&'
        else:
            url += '?'
        try:
            if len(paramDict) > 0: ## 如果有参数的话
                utf8_param = UnicodeUtil.convert_param_to_utf8(paramDict)
                url = "%s%s" % (url, urllib.urlencode(utf8_param))
        except Exception, e:
            url = None
            pass
    else:
        url = None
    return url

def getmd5(s):
    """
       return md5 hex ascii string for specific string.
    """
    import hashlib 
    if s == None: 
        return None 
    m = hashlib.md5() 
    m.update(s)
    return m.hexdigest()
    
if __name__ == '__main__':
    #makeDefaultDB()    
    kargs = {}
    success = getArg(kargs, 'success', 'hello')
    print success
    pass
    
