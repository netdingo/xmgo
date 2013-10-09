#coding=UTF-8
"""
xmgo prj, ver 0.0.2
xiti_db.py: handle sgf db
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


###import cjson ## shit, cjson does not work for object in object 
from UserDict import UserDict 
### import simplejson as sj ## shit, simplejson can not encode empty dict
import demjson
import os, sys
import time
import UnicodeUtil
import struct
import threading
import thread, hashlib, platform, base64
import tarfile
import httpret, FileUtility, UnicodeUtil, dbio
import public
import pdb
import cherrypy

def file_id(fn):
    utf8 = UnicodeUtil.get_utf8_str(fn)
    md5 = hashlib.md5(utf8)
    return md5.hexdigest()

class sgfdb:
    def __init__(self):
        pass

    def list_dir(self):
        assert(0)

    def load_sgf(self, fn):
        assert(0)

class SgfFileDB(sgfdb):
    def __init__(self, dbhome):
        self.dbhome = dbhome

    def list_dir(self):
        return FileUtility.listDir(self.dbhome, False, True)

    def load_sgf(self, fn):
        content = ""
        if fn :
            path = os.path.join(self.dbhome, fn)
            if FileUtility.fileExists(path):
                content = FileUtility.fileRead(path) 
        return content

class SgfTarDB(sgfdb):
    def __init__(self, subdir, dbf):
        self.subdir = subdir.lstrip("/").rstrip("/")
        self.dbf = dbf
        self.encoding_type = None
        if not tarfile.is_tarfile(self.dbf):
            print "%s is not a valid sgf tar db file!"
        else:
            self.get_tar_file_encoding()

    def get_tar_file_encoding(self):            
        try:
            tar = None
            tar = tarfile.open(self.dbf, "r:")
            for tarinfo in tar:
                if not self.encoding_type:
                    self.encoding_type = UnicodeUtil.get_encoding_type(tarinfo.name)
                break
        except Exception, e:
            print e
        finally:
            if tar : tar.close()

    def list_dir_1(self):
        try:
            dirs = []
            tar = None
            tar = tarfile.open(self.dbf, "r:")
            ##for name in tar.list(verbose = False):
            for name in tar.getnames():
                name = UnicodeUtil.get_unicode_str(name)
                if name.startswith(self.subdir):
                    d, f = os.path.split(name)
                    dirs.append(f)
                ##tar.extract(name,path=”/tmp”)
        except Exception, e:
            print e
        finally:
            if tar : tar.close()
        return dirs
        pass

    def list_dir(self):
        try:
            dirs = []
            tar = None
            tar = tarfile.open(self.dbf, "r:")
            for tarinfo in tar:
                #print tarinfo.name, "is", tarinfo.size, "bytes in size and is",
                name = UnicodeUtil.get_unicode_str(tarinfo.name)
                if name.startswith(self.subdir):
                    d, f = os.path.split(name)
                    dirs.append(f)
        except Exception, e:
            print e
        finally:
            if tar : tar.close()
        return dirs

    def load_sgf(self, fn):
        try:
            tar = None
            content = ""
            tar = tarfile.open(self.dbf, "r:")
            fn  = u"%s/%s" % (self.subdir, fn)
            if self.encoding_type: 
                et, et_s = self.encoding_type 
                fn = UnicodeUtil.get_specified_coding_string(fn, et)
            fo = tar.extractfile(fn)
            if fo:
                content = fo.read()
                fo.close()
        except Exception, e:
            print e
        finally:
            if tar : tar.close()
        return content 
        pass

    def create_db(self, dest_file, src_path, suffix = ["sgf", "sgf_"]):       
        try:
            tar  = None
            tar  = tarfile.open(dest_file,"w:") ##
            path = os.path.normpath(src_path.strip())
            for root, dir, files in os.walk(path):
                for fn in files:
                    if FileUtility.fileExt(fn) not in suffix: continue
                    fullpath = os.path.join(root, fn)
                    tar.add(fullpath)
        except Exception, e:
            print e
        finally:
            if tar : tar.close()
        pass

class SgfSqlDB(dbio.DBSQL, sgfdb):
    sgf_db = { 
    ## 习题集记录
    'sgf_xiti_set':[('id'  ,'INTEGER PRIMARY KEY AUTOINCREMENT'),
                    ('xiti_set_name','text NULL DEFAULT \'\''),
                    ('xiti_set_name_id','text NULL DEFAULT \'\''),
                   ],
    ## 习题集
    'sgf_xiti_files':[('id' ,        'INTEGER PRIMARY KEY AUTOINCREMENT'),
                      ('xiti_set_id','INTEGER DEFAULT 0'),     ## xiti set owner
                      ('file',       'INTEGER DEFAULT 0'),       ## file name
                      ('content',    'VARCHAR(24) NULL DEFAULT \'\''),                   ## file content
                     ],
    }
    def __init__(self, subdir, subdir_id, dbf):
        dbio.DBSQL.__init__(self, dbf)
        self.subdir = subdir 
        self.dbfile = dbf
        cherrypy.log.error(u"SgfSqlDB.__init__: subdir: %s, subdir_id: %s, dbf: %s" % (subdir, subdir_id, dbf) )
        self.subdir_id = subdir_id

    def list_dir(self):
        xid = self.get_xiti_set_id(self.subdir_id)
        if xid:
            ret = []
            cond = []
            cond.append(('xiti_set_id', xid))
            for rec in self.select('file', 'sgf_xiti_files', cond):
                fn = rec[0] if isinstance(rec, tuple) else rec
                ret.append(fn)
            return ret 
        else:
            return []

    def load_sgf(self, fn):
        xid = self.get_xiti_set_id(self.subdir_id)
        if xid:
            cond = []
            cond.append(('xiti_set_id', xid))
            cond.append(('file', fn))
            recs = self.select('content', 'sgf_xiti_files', cond)
            if recs and len(recs) > 0 :
                content = recs[0][0] if isinstance(recs[0], tuple) else recs[0]
                return base64.b64decode(content)
            else:
                cherrypy.log.error("SgfSqlDB.load_sgf: fail to read sgf for file : %s" % fn)
                return ""
        else:
            cherrypy.log.error("SgfSqlDB.load_sgf: fail to get xiti set id, fn: %s" % fn)
            return ""

    def get_xiti_set_id(self, fid):
        cond = []
        cond.append(('xiti_set_name_id', fid))
        recs = self.select('id', 'sgf_xiti_set', cond)
        if recs and len(recs) > 0 :
            rec = recs[0]
            return int(rec[0])
        else:
            cherrypy.log.error("SgfSqlDB.get_xiti_set_id: fail, fid: %s, recs: %s" % (fid, repr(recs)))
            return None

    def add_xiti_set(self, path, fid): 
        """
            记录sgf_xiti_set表。
        """
        xid = self.get_xiti_set_id(fid)
        if not xid:
            rec = {} 
            rec['xiti_set_name'] = path
            rec['xiti_set_name_id'] = fid
            self.insert('sgf_xiti_set', rec)

    def get_file_base64_content(self, fn):
        content = FileUtility.fileRead(fn) 
        if content:
            return base64.b64encode(content)
        else:
            return None

    def add_xiti(self, fid, fn): 
        xid = self.get_xiti_set_id(fid)
        content = self.get_file_base64_content(fn)
        if xid and content:
            rec = {}
            rec['xiti_set_id'] = xid
            f1, pf = os.path.split(fn)
            rec['file'] = pf
            rec['content'] = content
            self.insert('sgf_xiti_files', rec)

    def createTable(self):
        for table_name, fields in SgfSqlDB.sgf_db.items(): 
            self.createTable(table_name, fields)

    def create_db(self, src_path, suffix = ["sgf", "sgf_"]):
        logdb_file = self.dbfile
        if os.path.exists(logdb_file):
            import FileUtility as fu
            dirname = os.path.dirname(logdb_file)
            if not fu.pathExists(dirname):
                fu.createPath(dirname)
            self.createTable()
        for p in FileUtility.listAll(src_path, just_directory = True, contain_file = True):
            norm_p = p.replace("\\", "/") 
            if not norm_p.startswith("/"): norm_p = "/" + norm_p
            norm_p = UnicodeUtil.get_unicode_str(norm_p)
            xiti_set_saved = False
            fp = os.path.join(src_path, p.lstrip(os.path.sep))
            fp = UnicodeUtil.get_unicode_str(fp)
            for fn in FileUtility.listfiles(fp):
                #print fn
                if FileUtility.fileExt(fn) not in suffix: continue
                if xiti_set_saved == False:
                    fid = file_id(norm_p) 
                    self.add_xiti_set(norm_p, fid)
                    xiti_set_saved = True
                fn = os.path.join(fp, fn)
                self.add_xiti(fid, fn)

class XitiDB(UserDict):
    """
       习题数据库，基类，习题数据库目前采用文件系统，但习题多是小文件，数量多了，
       复制，管理比较麻烦，可以用tar文件将其集中起来，或用sqlite来管理。
    """
    def __init__(self, xiti_set_subpath, **kargs):
        dbhome    = public.get_arg("dbhome", kargs, public.XITI_DB_HOME)
        self.xiti_set_id = file_id(xiti_set_subpath)
        self.dbfile      = os.path.join(dbhome, self.xiti_set_id)
        self.sgf_db      = self.create_sgf_db(xiti_set_subpath, **kargs)
        self.initDB()
        db = self.loadDB()
        UserDict.__init__(self, db)
        pass

    def is_abs_path(self, path):
        fn = os.path.abspath(os.path.normpath(path))
        if platform.system() == 'Windows':
            return fn.startswith(path) ##TODO 
        else:
            return path.startswith("/")

    def get_norm_path(self, path):
        if platform.system() == 'Windows':
            return os.path.abspath(os.path.normpath(path))
        else:
            return os.path.abspath(path.replace("\\", "/")) ## os.path.normpath does not work in my pc

    def create_sgf_db(self, xiti_set_subpath, **kargs): 
        ## default sgf db type: file
        sgf_type   = public.get_arg("sgf_db_type", kargs, public.SGF_DB_FILE)
        ## default home  ../sgf
        xiti_home  = public.get_arg("xiti_home", kargs, public.XITI_HOME) 
        real_path  = os.path.join(xiti_home, os.path.normpath(xiti_set_subpath).lstrip(os.path.sep))
        if sgf_type == public.SGF_DB_FILE:
            return SgfFileDB(real_path)
        dbf = public.get_arg("sgf_db", kargs, public.SGF_DB) ## default sgf tar db : sgf.tar
        if not self.is_abs_path(dbf):
            dbf = os.path.join(os.path.normpath(xiti_home), os.path.normpath(dbf).lstrip(os.path.sep)) ## default full sgf tar db: ..\sgf\sgf.tar
        dbf = self.get_norm_path(dbf)
        if sgf_type == public.SGF_DB_TAR: 
            return SgfTarDB(xiti_set_subpath, dbf)
        if sgf_type == public.SGF_DB_SQL: 
            return SgfSqlDB(xiti_set_subpath, self.xiti_set_id, dbf)
        else:
            return None

    def get_dbfile(self):
        return self.dbfile

    def initDB(self):
        """
          初始化每个习题集的数据库，不要sqlite的原因如下：
              1）sqlite在cubieboard等板子中速度较慢。
              2）sqlite不支持多线程。
          每个习题集用一个json数据库文件, 文件名用md5归一化，加载前
          先初始化。该数据库文件格式如下：
          {
            sum: xx,
            finish_sum: xx,
            current_num: xx,
            files:{
                <fn1>: { s : 0 | 1,   ## status：0：未完成，1：已完成
                         t1: xxx,     ## start time 开始答题时间，以秒为单位
                         t2: xxx,     ## end time   结束答题时间
                         c : 0 | 1,   ## crypt      0：未加密，1：已加密
                         n : yyy,     ## file index number 题目编号
                         st : xx,     ## 行棋的步骤
                         tr : xx,     ## 尝试的步骤
                         d  : 0 | 1   ## 是否看了答案
                       },  
                <fn2>: { s : 0 | 1,   ## status
                         t1: xxx,     ## start time
                         t2: xxx,     ## end time
                         c : 0 | 1,   ## crypt
                         n : yyy,     ## file index number
                         st : xx,     ## 行棋的步骤
                         tr : xx,     ## 尝试的步骤
                         d  : 0 | 1   ## 是否看了答案
                       },  
                ....
            }
          }
        """
        if FileUtility.fileExists(self.dbfile): return True
        db = {}
        files = {}
        count  = 0
        finish = 0
        current= 0
        for fn in self.sgf_db.list_dir():
            crypt = self.is_sgf_file(fn)
            if None == crypt: continue
            files[fn] = {}
            files[fn]['c'] = crypt ## crypt
            files[fn]['s'] = 0     ## status
            files[fn]['t1']= 0     ## start time
            files[fn]['t2']= 0     ## end time
            files[fn]['n'] = count ## fn index
            count += 1
        db['sum']        = count
        db['finish_sum'] = finish 
        db['current_num']= current 
        db['files']      = files
        self.saveDB(self.dbfile, db)
        del db

    def is_sgf_file(self, fn):
        ext = FileUtility.fileExt(fn)
        if ext == 'sgf': 
            ret = 0
        elif ext == 'sgf_':
            ret = 1
        else:
            ret = None
        return ret

    def load_sgf(self, fn):
        return self.sgf_db.load_sgf(fn)

    def saveDB(self, fn = None, db = None):
        confdb = self if db == None else db
        dfn = self.dbfile if fn == None else fn
        dbf = file(dfn, "w")
        #dbf.write(demjson.encode(confdb)
        dbf.write(demjson.encode(confdb, escape_unicode=False, encoding='ascii'))
        dbf.close()

    def loadDB(self): 
        confdb = None
        try:
            dbf = file(self.dbfile, "r")
            if dbf == None:
                print "Fail to load ",  self.dbfile
                return None 
            db = dbf.read()
            try:
                confdb = demjson.decode(db)
            except demjson.JSONDecodeError, e: 
                confdb = None
                pass
            dbf.close()
        except IOError, e:
            print "Fail to load db from %s"%(self.dbfile)
        return confdb
        pass
    def get_info(self):
        count = self['sum'] if 'sum' in self else 0
        finish = self['finish_sum'] if 'finish_sum' in self else 0
        current = self['current_num'] if 'current_num' in self else 0
        return (count, finish, current)

    def get_specified_sgf(self, inc, **kargs):
        key = "new_number"
        abs_num = kargs[key] if key in kargs else None 
        key = "pass_chk"
        pass_chk= kargs[key] if key in kargs else 0 
        count, finish, current = self.get_info()
        old_current = current
        if count == 0:
            return None
        else:
            if abs_num != None: ## specify mode
                pass_chk = 0 ## for specify feature, ignore pass_chk
                if abs_num < count and abs_num >= 0:
                    current = abs_num
                else:
                    return None
            else:
                if inc == 0: pass_chk = 0 ## for current function, ignore pass_chk
                current += inc 
                current = current % count
            ret = {}
            for fn in self['files']:
                rec = self['files'][fn]
                bingo = 0
                if pass_chk == 1 and int(rec['s']) != 1:  ## check pass_chk firstly
                    if inc == 1 and int(rec['n']) > old_current:
                        bingo = 1
                        current = int(rec['n'])
                    elif inc == -1 and int(rec['n']) < old_current:
                        bingo = 1
                        current = int(rec['n'])
                elif pass_chk == 0 and int(rec['n']) == current:
                    bingo = 1
                else:
                    bingo = 0
                if bingo == 1:
                    ret['crypt']  = int(rec['c'])
                    ret['status'] = int(rec['s'])
                    ret['fn']     = fn 
                    ret['rec']    = rec
                    break
            ret['current_num'] = current
            ret['finish_sum']  = finish
            self['current_num']= current
            return ret        

    def current(self, **args):
        return self.get_specified_sgf(0)

    def prev(self, **args):
        key = 'pass_chk'
        pass_chk = args[key] if key in args else 0 
        return self.get_specified_sgf(-1, pass_chk = pass_chk)

    def next(self, **args):
        key = 'pass_chk'
        pass_chk = args[key] if key in args else 0
        return self.get_specified_sgf(1, pass_chk = pass_chk)

    def specify(self, **args):
        key = 'new_number'
        new_number = args[key] if key in args else -1
        return self.get_specified_sgf(0, new_number = new_number)

    def add_finish_count(self, current_num, inc):
        self['finish_sum'] += inc
        self['current_num'] = current_num

def test_tar_db():        
    dbn = "sgf.tar" 
    path = UnicodeUtil.get_unicode_str("/围棋入门-基本技能训练/抱吃/")
    tdb = SgfTarDB(path, dbn)
    ##print tdb.list_dir()
    msg = tdb.load_sgf("0.sgf_")
    print msg

def create_sgf_sql_db(*argv): 
    if len(argv) != 3: 
        print """ python xiti_db_py <src sgf path> <dest sqlite db> """
        sys.exit(0)
    src = sys.argv[1]
    dest_db = sys.argv[2]
    db = SgfSqlDB("/test", "test_id", dest_db) 
    db.create_db(src)

if __name__ == '__main__':
    create_sgf_sql_db(*(sys.argv))
    pass
