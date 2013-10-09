#coding=UTF-8
"""
xmgo prj, ver 0.0.2
controller.py: controller 
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

from UserDict import UserDict 
import demjson
import os, sys
import time
import UnicodeUtil
import struct
import threading
import thread
import httpret
import pdb

class CommandController():
    admin = None
    items = {}
    def __init__(self):
        self.dispatchMutex = thread.allocate_lock()
        CommandController.admin = self
        pass

    def get_admin(self):
        return CommandController.admin

    def get_item(self, name):
        if name in CommandController.items:
            return CommandController.items[name]
        else:
            return None

    @classmethod
    def register(cls, item_name, item_cls):
        if item_name not in CommandController.items:
            admin = CommandController.admin
            if admin == None:
                CommandController()
            CommandController.items[item_name] = item_cls(CommandController.admin)

    def returnResult(self, result, info):
        return httpret.createHttpReturn('ajax', success=result, info=info)

    def dispatchLock(self):
        self.dispatchMutex.acquire()
        pass

    def dispatchUnlock(self):
        self.dispatchMutex.release()
        pass

    def dispatch(self, item, cmd, args):
        """
           dispatch http://xxx/xmgo?item=xx&cmd=xx 命令
        """
        try:
            self.dispatchLock()
            ret = self.do_dispatch(item, cmd, args)
        finally:
            self.dispatchUnlock()
        return ret            
        pass

    def shutdown(self):
        pass

    def do_dispatch(self, item, cmd, args):
        if item in CommandController.items:
            item_obj = CommandController.items[item]
            if item_obj and hasattr(item_obj, cmd): ## 检查命令是否在类方法中存在
                method = getattr(item_obj, cmd)
                assert method != None, "class %s has no method %s!"%(item, cmd)
                argstr = ""
                start  = 1
                for k in args.keys():
                    #ignore the key work we don't know
                    if  not item_obj.isValidParam(k): continue
                    val = UnicodeUtil.convert_param_to_unicode(args[k], False)
                    if isinstance(val, str) or isinstance(val, unicode):
                        val = val.strip()
                    val = repr(val)
                    if start == 1:
                        argstr = "%s %s=%s"%(argstr, k, val)
                    else:
                        argstr = "%s, %s=%s"%(argstr, k, val)
                    start = 0    
                cmdstr = "method(%s)"%(argstr)
                retval = eval(cmdstr) ## 执行命令
                return retval
        return self.returnResult(False, u"无效的管理命令!")

if __name__ == '__main__':
    pass
