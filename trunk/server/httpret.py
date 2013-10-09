#coding=UTF-8
"""
xmgo prj, ver 0.0.2
httpret.py: http return result, for example, extjs record and so on.
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


import os,sys
import demjson
import pdb
import misc
import UnicodeUtil

class httpRetRecord:
    def __init__(self):
        pass

    def py2json(self, retval):
        """
           将python值转为utf-8后返回。
        """
        return demjson.encode(retval, escape_unicode=False, encoding='utf8')

    def bool2str(self, value):
        return self.py2json(value)

    def bool2int(self, value):
        if value: return 1
        else    : return 0

    def getUTF8(self, ustr):
        """
            转换为UTF8, 不用demjson的原因是，demjson转换的UTF8字符串被""包括起来，
            造成，浏览器识别错误。
        """
        if isinstance(ustr, unicode): 
            return ustr.encode('UTF-8')
        else:
            return ustr

    def dictItem2str(self, **kargs):        
        item_list = []
        for key, value in kargs.items():
            if isinstance(value, bool):
                value = self.bool2str(value)
            item_list.append("\"%s\":\"%s\"" % (key, value))
        if len(item_list) > 0:
            return ",".join(item_list)
        else:
            return "" 

    def getStringReturn(self, value):
        if isinstance(value, str) :
            return value
        elif isinstance(value, unicode) :
            return self.getUTF8(value) 
        else:
            return self.py2json(value)

    def getmsg(self): ## 需要重载
        assert(0)
        pass

class extForm(httpRetRecord):
    """
       返回ext form记录。
    """
    def __init__(self, success, data):
        httpRetRecord.__init__(self)
        self.ret = success
        self.data = data ## data可能已经是字典或列表对象

    def getData(self):
        return self.data

    def getmsg(self):
        d = {'success':self.bool2str(self.ret), 'data':self.data}
        return self.py2json(d) ##将数据对象转换json格式

class extComboRecord(httpRetRecord):
    """
       返回combo记录。
    """
    def __init__(self, data):
        httpRetRecord.__init__(self)
        self.data = data ## data可能已经是字典或列表对象

    def getRecords(self):
        return self.data

    def getmsg(self):
        return self.py2json(self.data) ##将数据对象转换json格式

class extGrid(httpRetRecord):
    """
       返回ext Grid 数据
    """
    def __init__(self, totalCount, data):
        httpRetRecord.__init__(self)
        retval = {}
        if totalCount == None:
            totalCount = len(data)
        retval['totalCount'] = totalCount 
        retval['values']     = data
        self.recs = retval

    def getRecords(self):
        return self.recs

    def getmsg(self):
        return self.py2json(self.recs) ##将数据对象转换json格式

class extJsonStoreRecord(httpRetRecord):
    """
       返回extjs 记录，类似用 Ext.data.JsonStore 来取的数据
    """
    def __init__(self, record):
        self.data = [ record ]

    def getRecords(self):
        return self.data

    def getmsg(self):
        return self.py2json(self.data)


class extAjaxReturn(httpRetRecord):
    """
       返回ext ajax 记录，类似用 Ext.data.JsonStore 来取的数据
    """
    def __init__(self, success, info, event=None):
        httpRetRecord.__init__(self)
        self.ret     = success
        #self.info   = self.getUTF8(info)
        #self.event  = self.getUTF8(event)
        self.info    = info
        self.event   = event

    def getmsg(self):
        d = {'success': self.ret,  #self.bool2str(self.ret), 
             'info'   : self.info 
            }
        if self.event != None:
            d ['event'] = self.event
        return self.py2json(d)

class stringReturn(httpRetRecord):
    """
       返回字符串。
    """
    def __init__(self, msg):
        httpRetRecord.__init__(self)
        self.msg = msg

    def getmsg(self):
        return self.getStringReturn(self.msg)

class psManualReturn(httpRetRecord):            
    """
       返回手册内容。
    """
    def __init__(self, msg):
        httpRetRecord.__init__(self)
        self.msg = msg

    def getmsg(self):
        return self.getStringReturn(self.msg)

class psBootAgentReturn(httpRetRecord):
    def __init__(self,  **kargs):
        httpRetRecord.__init__(self)
        self.success = self.bool2int(kargs['success'])
        self.info    = kargs['info']
        del kargs['success']
        del kargs['info']
        self.kargs   = kargs

    def getmsg(self):
        msg = "success=%d;info=%s"%(self.success, self.info)
        kargs = self.kargs
        if len(kargs) > 0:
            for key in kargs.keys():
                if isinstance(kargs[key], list):
                    for item in kargs[key]:
                        if isinstance(item, str) or isinstance(item, unicode) :
                            msg="%s;%s=%s"%(msg, key, item)
                        else:
                            msg="%s;%s=%d"%(msg, key, item)
                else:
                    if isinstance(kargs[key], str) or isinstance(kargs[key], unicode):
                        msg="%s;%s=%s"%(msg, key, kargs[key])
                    else:
                        msg="%s;%s=%d"%(msg, key, kargs[key])
        ## for boot agent return, don't convert it python value                            
        msg = UnicodeUtil.get_ascii_str(msg) 
        return msg

def createHttpReturn(retType, **kargs):
    """
       根据retType类型创建httpret.httpRetRecord类型
       参数：
           'success': extjs要求的返回值，一般是'ajax'返回类型的强制参数
           'event'  : 可选参数
           'info'   : 当retType是'ajax'时，其一般是extjs要求的返回信息，此时
                      其为强制，如果retType是'str'时，其表示直接返回的字符串。
           'data'   : ext grid，JsonStore或其他格式要求返回的数据带一定格式
    """
    success = misc.getArg(kargs, 'success', None)
    info    = misc.getArg(kargs, 'info', None)
    event   = misc.getArg(kargs, 'event', None)
    data    = misc.getArg(kargs, 'data', None)
    if retType == 'str': ## 只返回字符串
        result = stringReturn(info)
    elif retType == 'ajax': ##返回ajax 记录
        result = extAjaxReturn(success, info, event)
    elif retType == 'boot_agent': ##返回ajax 记录
        result = psBootAgentReturn(**kargs)
    elif retType == 'ext_form': ##返回ext form 记录
        result = extForm(success, data)
    elif retType == 'ext_record': ##返回ext form 记录
        result = extJsonStoreRecord(data)
    elif retType == 'ext_grid': ##返回ext form 记录
        totalCount = misc.getArg(kargs, 'totalCount', None)
        result = extGrid(totalCount, data)
    elif retType == 'combo_record': ##返回combo记录
        result = extComboRecord(data)
    elif retType == 'manual':       ## 返回手册内容
        result = psManualReturn(info)
    else:
        result = extAjaxReturn(success, info, event)
    return result
    
if __name__ == '__main__':
    s = createHttpReturn('str', info='hello')
    print s
