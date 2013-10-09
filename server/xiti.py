#coding=UTF-8
"""
xmgo prj, ver 0.0.2
xiti.py:  load GO xiti
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

###import cjson ## shit, cjson does not work for object in object 
from UserDict import UserDict 
### import simplejson as sj ## shit, simplejson can not encode empty dict
import demjson
import os, sys
import time
import UnicodeUtil
import struct
import threading
import thread, hashlib
import public
import httpret, FileUtility, UnicodeUtil
import xiti_db
import cherrypy
import pdb

class XitiConf():
    def __init__(self, conf = public.XITI_CONF):
        self.conf = conf
        self.xiti_home = None
        self.conf_vars = { "xiti_home":None, "sgf_db":None, "sgf_db_type":None, "xiti_conf": []}
        self.load_conf()

    def get_conf_vars(self):
        return self.conf_vars

    def load_conf(self):
        try:
            conf = FileUtility.readFile(self.conf).replace("\r", "")
            exec conf
            gl = locals()
            for var in self.conf_vars.keys():
                if gl.has_key(var):
                    self.conf_vars[var] = gl[var]
            ## patch xiti_home, because run as daemon, which need full path
            if 'xiti_home' in self.conf_vars:
                xiti_home = self.conf_vars['xiti_home']
                conf_path, pf = os.path.split(self.conf)
                if not os.path.isabs(xiti_home):
                    xiti_home = os.path.normpath(os.path.join(conf_path, xiti_home))
                    self.conf_vars['xiti_home'] = xiti_home
            self.xiti_conf = [ ["" ,  self.conf_vars['xiti_conf'] ] ]
            del self.conf_vars['xiti_conf']
        except Exception, e:
            print e
        pass

    def listDir(self, full_path, dirs = True):
        full_path = os.path.normpath(full_path)
        sep = os.path.sep
        if full_path != sep:
            path = full_path.rstrip(sep)
            path_items = path.split(sep) 
        else: 
            path_items = [""]
        temp = self.xiti_conf 
        for p in path_items: 
            p = UnicodeUtil.get_unicode_str(p)
            found = False
            for x in temp:
                if isinstance(x, list):
                    key, l = x
                else:
                    key = x
                    l = []
                if p == UnicodeUtil.get_unicode_str(key):
                    temp = l
                    found = True
                    break
            if not found : assert(False)
        ret = []
        for i in temp:
            if isinstance(i, list):
                key, l = i
                ret.append((UnicodeUtil.get_unicode_str(key), False))
            elif isinstance(i, str) or isinstance(i, unicode):
                ret.append((UnicodeUtil.get_unicode_str(i), True))
        return ret
    

class XitiItem():
    def __init__(self, admin):
        self.admin = admin
        self.xiti_conf = XitiConf()
        self.selected_path    = None
        self.selected_xiti_db = None
        self.selected_sgf     = None
        pass

    def isValidParam(self, arg):
        ##TODO
        return True

    def select(self, **args):
        """
        选择习题集：
        返回记录的格式：
           { success: True|False,
             info: {  sum: <>,
                      finish_sum: <>,
                      current_num: <>,
                      err: <>, }
           } 
        """
        path = args['dir'].rstrip("/")
        if path != self.selected_path :
            self.selected_path    = path
            if  self.selected_xiti_db: self.selected_xiti_db.saveDB() ## save old xiti set 
            conf_vars = self.xiti_conf.get_conf_vars()
            try:
                self.selected_xiti_db = xiti_db.XitiDB( path, 
                                                        xiti_home = conf_vars['xiti_home'], 
                                                        sgf_db    = conf_vars['sgf_db'],  
                                                        sgf_db_type = conf_vars['sgf_db_type'],  
                                                      )
            except Exception, e:
                print e
                self.selected_xiti_db = None
                ret_data = { }
                ret_data['err'] = u"Fail to create XitiDB!"
                return httpret.createHttpReturn('ajax', success= False, info= ret_data)
        ret_data = { }
        ret = True
        count, finish, current = self.selected_xiti_db.get_info()
        ret_data['sum'] = count 
        ret_data['finish_sum'] = finish 
        ret_data['current_num'] = current
        ret_data['err'] = u""
        return httpret.createHttpReturn('ajax', success= ret, info= ret_data)

    def list(self, **args):
        if args.has_key('sendWhat') :
            dir_type = args['sendWhat']
        else:
            dir_type = 'dirs'
        return self.get_xiti(args['dir'], dir_type)

    def select_sgf(self, **args):
        """
           webui 从当前习题集中选择：当前/前一个/下一个 题目
               args: {
                   sgf_item: 'current' | 'next' | 'prev' | 'specify',
                   new_number: <new xiti number>
                   pass_chk :  < 0 | 1 > ## 1: 跳过已完成题目
               }
           返回数据格式：
               {
                   current_num: xx,
                   finish_sum : xx,
                   crypt: 0 | 1,
                   status: 0 | 1,
               }
        """
        sgf_item = args['sgf_item']
        db = self.selected_xiti_db
        ret = False
        ret_data = {}
        if db and hasattr(db, sgf_item):
            method = getattr(db, sgf_item)
            new_args = {}
            if 'new_number' in args:
                new_args['new_number'] = int(args['new_number'])
                errmsg = u"Fail to specify new xiti number: %d" % new_args['new_number']
            else:
                errmsg = u"Fail to jump to xiti number!"
            new_args['pass_chk'] = int(args['pass_chk'])
            sgf = method(**new_args)
            if sgf and "rec" in sgf:
                self.selected_sgf = sgf
                ret = True
                ret_data['current_num'] = sgf['current_num']
                ret_data['finish_sum']  = sgf['finish_sum'] 
                ret_data['crypt']       = sgf['crypt']
                ret_data['status']      = sgf['status']
            else:
                ret = False
                if errmsg : ret_data['err'] =  errmsg
        return httpret.createHttpReturn('ajax', success = ret, info= ret_data)

    def load_sgf(self, **args):
        """
          goxiti.swf 加载sgf
          参数：{
                sgf_num
            }
        """
        sgf_num = args['sgf_num'] if 'sgf_num' in args else 0 
        crypt   = args['crypt'] if 'crypt' in args else 0 
        sgfurl  = args['sgfurl'] if 'sgfurl' in args else None
        content = ""
        if self.selected_sgf:
            fn      = self.selected_sgf['fn']
            current_num = self.selected_sgf['current_num']
            content = self.selected_xiti_db.load_sgf(fn) ## 
            if content != "":
                if 't1' not in self.selected_sgf: 
                    self.selected_sgf['t1'] = int(time.time()) 
                    self.selected_sgf['t2'] = 0
            else:
                cherrypy.log.error(msg= "load_sgf: fail to load sgf")
        else:
            cherrypy.log.error(msg= "load_sgf: selected_sgf is None!" )
        return content

    def send_info(self, **args):
        """
           webui 调用，用来发送走棋步数，尝试次数，下棋结果等
           args 参数如下：
           {
             steps: current_steps,   ## 步数
             trys: current_trys,     ## 步骤数
             result: current_result, ## 结果
             demo : saw_demo         ## 是否看了演示
           }
        """
        def get_args(args):
            def single_arg(args, name):
                return args[name] if name in args else 0 
            steps = int(single_arg(args, "step"))
            trys  = int(single_arg(args, "trys"))
            result= int(single_arg(args, "result"))
            demo  = int(single_arg(args, "demo"))
            return (steps, trys, result, demo)

        ret = False
        ret_data = {}
        if self.selected_sgf:
            current_num = self.selected_sgf['current_num']
            steps, trys, result, demo = get_args(args) 
#            self.selected_sgf['steps'] = steps
#            self.selected_sgf['trys']  = trys 
#            self.selected_sgf['result']= result 
#            self.selected_sgf['demo']  = demo
            if result != -1:
                t1 = t2 = 0
                rec  = self.selected_sgf['rec']
                if 't2' in self.selected_sgf and 't1' in self.selected_sgf:
                    self.selected_sgf['t2'] = int(time.time()) 
                    t1 = self.selected_sgf['t1']
                    t2 = self.selected_sgf['t2']
                if  self.selected_xiti_db: 
                    if rec :
                        if rec['s'] != 1 and result == 1: 
                            self.selected_xiti_db.add_finish_count(self.selected_sgf['current_num'], 1)
                        elif rec['s'] == 1 and result == 0:  
                            self.selected_xiti_db.add_finish_count(self.selected_sgf['current_num'], -1)
                    self.selected_xiti_db.saveDB() ## save xiti set 
                rec['t1'] = t1
                rec['t2'] = t2
                rec['st'] = steps
                rec['tr'] = trys 
                rec['s']  = result
                rec['d']  = demo
                ret = True
        return httpret.createHttpReturn('ajax', success= ret, info= ret_data)
        

    def get_xiti(self, path, dir_type="dirs"):
        just_directory = True 
        if dir_type == 'both':      ## 应该是file grid store的请求
            just_directory = False
        filelist = self.xiti_conf.listDir(path, just_directory)
        return self.getTreeRecords(filelist)

    def getTreeRecords(self, pathList=[]):
        """
           生成tree node 记录格式  
        """
        tree=[]
        for path, isLeaf in pathList:
            node = self.make_tree_node(path, None, None, isLeaf)
            if isLeaf :
                node["iconCls"] = "tree-node-FilePanel"
            tree.append(node)
        return httpret.createHttpReturn('combo_record', data=tree)

    def make_tree_node(self, text, id, cls, isLeaf):
        node = {}
        node['text'] = text
        if id  != None: node['id']   = id 
        if cls != None: node['cls']  = cls
        if isLeaf     : node['leaf'] = isLeaf 
        node['editable'] = False
        ####node['t'] = node_type ## '1': user, '0': os, '2'
        return node

    def returnResult(self, result, info):
        return httpret.createHttpReturn('ajax', success=result, info=info)

    def verify_client_cmd(self, cmd, valid_command_set):
        if cmd not in valid_command_set:
            return self.returnResult(False, u"无效的客户端命令!")
        else:
            return (True, "")

from controller import CommandController
CommandController.register('xiti', XitiItem)

if __name__ == '__main__':
    pass
