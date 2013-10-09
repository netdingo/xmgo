#!/usr/bin/python
#coding=UTF-8
"""
xmgo prj, ver 0.0.2
dbio.py: sqlite module
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
import FileUtility
from   misc import *
from   threading import Thread
from   Queue import Queue
import public
import pdb

import platform
isLinux = platform.system() != 'Windows'  
TRACE_DB=False

class DBSQL:
    def __init__(self, dbfile=None):
        if dbfile != None:
            self.dbfile = dbfile 
        else:
            self.dbfile = public.DB_FILE 
        if not FileUtility.fileExists(self.dbfile):
            FileUtility.createFile(self.dbfile)
        self.conn = None
        self.cursor = None
        self.conn_failed = False 

    def __del__(self):
        ##self.closeDB()
        pass

    def connect(self):
        try:
            import sqlite3
        except Exception, e:
            print "Fail to import sqlite3!"
            self.conn_failed = True
            return (None, None)
            pass
        i = 0
        while i < 1000:
            try:
                self.conn = sqlite3.connect(self.dbfile, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, timeout=1)
                self.conn_failed = False 
                return (self.conn, self.conn.cursor())
            except Exception, e:
                pass
            i += 1
        return (None, None)
 
    def free(self, cursor):
        if cursor:
            cursor.close()
 
    def closeDB(self):
        if self.conn: self.conn.close()
        self.conn = None

    def close(self):        
        self.closeDB()

    def execute(self, req, arg=None, res=None):
        if TRACE_DB: print "execSql: ", req
        try:
            conn, cursor = self.connect()
            if self.conn_failed or conn == None:
                print "Fail to execute: ", req
                print "Reason: Fail to connect db: ", self.dbfile
                return None
            if arg:
                cursor.execute(req, arg)
            else:
                cursor.execute(req)
        except Exception, e:
            print Exception, e
            pass
        if res and cursor:
            for rec in cursor:
                res.put(rec)
        if conn: self.commit(conn)
        if cursor: self.free(cursor)

    def execSql(self, sql):
        return self.execute(sql)

    def selectSql(self, req, arg=None):
        res=Queue()
        self.execute(req, arg, res) 
        while not res.empty():
            rec = res.get()
            yield rec

    def commit(self, conn):
        if conn: return conn.commit()
        else: return None

    def checkValue(self, **args):
        for key, value in args:
            if value == None : return False
            if len(value) == 0 : return False
        return True

    def list2str(self, vlist, quote=None, split_mark =None):
        first = True
        v = ""
        if split_mark == None : split_mark = " , "
        else: split_mark = " %s "%split_mark
        for value in vlist:
            if first :
                split = " "
                first = False
            else:
                split = split_mark
            if isinstance(value, unicode):
                value = value.encode("utf-8")
            if isinstance(value, str): 
                #value = value.replace("\'", '\'\'')
                #value = value.replace("\"", "\\\"")
                try:
                    if quote != None:
                        v = v + split + quote + value + quote
                    else:
                        v = v + split + value
                except Exception, e:
                    print e
                    pass
            elif isinstance(value, long):
                v = v + "%s %s"%(split, value) #hex(value)
            else:
                v = v + split + repr(value)
        return v

    def createTable(self, name, fields):
        """
            format: 
                name: table name
                fields: [(field1, type), (field2, type)...]
        """
        if self.checkValue(v1 = name, v2 = fields) == False:
            return False
        fv = []
        for field, field_type in fields:
            fv.append("%s %s"%(field, field_type))
        fv_list = self.list2str(fv)
        sql = 'create table %s ( %s )'%(name, fv_list)
        return self.execSql(sql)

    def insert(self, table, values):
        """
            format:
                table: table name
                values: if dict : like {field_name:field_value, ...}
                        if tuple: like (field_value1, field_value2, ...)
        """
        if self.checkValue(v1 = table, v2 = values) == False:
            return False
        kl = []
        vl = []
        if isinstance(values, dict):
            for key, value in values.items():
                kl.append(key)
                vl.append(value)
            field_list = self.list2str(kl)
            value_list = self.list2str(vl, "\'")
            sql = "INSERT INTO %s( %s ) VALUES( %s )"%(table, field_list, value_list)
        elif isinstance(values, tuple):
            value_list = self.list2str(values, "\'")
            sql = "INSERT INTO %s VALUES ( %s )"%(table, value_list)
        else:
            sql = None
        if sql != None:
            return self.execSql(sql)
        else:
            return None 

    def update(self, table, fields, conditions = None):
        """
            format: 
                table    : table name
                fields   : [ (field1 , value1), (field2 , value2),... ]
                condition: [ (field1 , value1), (field2 , value2),... ]
        """                      
        if self.checkValue(v1 = table, v2 = fields) == False:
            return False
        if not isinstance(fields, list): return False
        ## construct fields value string
        f_list = [] 
        for f, v in fields:
            for f, v in fields:
                if isinstance(v, str) or isinstance(v, unicode):
                    f_list.append("%s = \'%s\'"%(f, v))
                else:
                    f_list.append("%s = %s"%(f, v))
        if len(f_list) > 0:
            field_list = self.list2str(f_list)
        else:
            field_list = ""
        ## construct condistion string
        cond_list = []
        if conditions != None:
            for f, v in conditions:
                if isinstance(v, str) or isinstance(v, unicode):
                    cond_list.append("%s = \'%s\'"%(f, v))
                else:
                    cond_list.append("%s = %s"%(f, v))
        if len(cond_list) > 0 :
            condition_list = "WHERE " + self.list2str(cond_list, None, 'AND') 
        else:
            condition_list = ""
        sql = "UPDATE %s SET %s %s "%(table, field_list, condition_list) 
        self.execSql(sql)

    def select(self, fields, tables, conditions = None):
        """
            format: 
                fields : '*', single field, or query field list
                tables : single table or query table list
                condition: ( (field1 , value1), (field2 , value2),... )
        """                      
        if self.checkValue(v1 = fields, v2 = tables) == False:
            return False
        if isinstance(fields, list): 
            field_list = self.list2str(fields) 
        else:
            field_list = fields
        if isinstance(tables, list): 
            table_list = self.list2str(tables, '\`') 
        else:
            table_list = tables
        cond_list = []
        if conditions != None:
            for f, v in conditions:
                if isinstance(v, str) or isinstance(v, unicode):
                    cond_list.append("%s = \'%s\'"%(f, v))
                else:
                    cond_list.append("%s = %s"%(f, v))
        if len(cond_list) > 0 :
            condition_list = "WHERE " + self.list2str(cond_list, None, 'AND') 
        else:
            condition_list = ""
        sql = "SELECT %s FROM %s %s"%(field_list, table_list, condition_list) 
        recs = []
        for rec in self.selectSql(sql):
            recs.append(rec)
        return recs

    def delete(self, tables, conditions = None):
        """
            从表中删除记录。
            format: 
                tables : single table or query table list
                condition: 可以是如下格式：
                   1)   [ (field1 , value1), (field2 , value2),... ]
                   2)   [  cond1, cond2, ... ]
                   3)   condition
        """
        if isinstance(tables, list): 
            table_list = self.list2str(tables, '\`') 
        else:
            table_list = tables
        cond_list = []
        if isinstance(conditions, list):
            for item in conditions:
                if isinstance(item, tuple) or isinstance(item, list):
                    f, v = item
                    if isinstance(v, str) or isinstance(v, unicode):
                        cond_list.append("%s = \'%s\'"%(f, v))
                    else:
                        cond_list.append("%s = %s"%(f, v))
                else:
                    cond_list.append(item)
        elif isinstance(conditions, str) or isinstance(conditions, unicode):
            cond_list = [ conditions ]
        if len(cond_list) > 0 :
            condition_list = "WHERE " + self.list2str(cond_list, None, 'AND')
        else:
            condition_list = ""
        sql = "DELETE FROM %s %s"%(table_list, condition_list)
        self.execSql(sql)

class DB(DBSQL, Thread):
    def __init__(self, dbfile=None):
        DBSQL.__init__(self, dbfile)
        Thread.__init__(self)
        self.cond = threading.Condition()
        self.reqs=Queue()
        self.start()

    def __del__(self):
        self.closeDB()
        print "sqlite3 thread exit!\n"

    def run(self):
        self.cond.acquire()
        self.conn, self.cursor = self.connect()
        if TRACE_DB: print "begin to run sqlite3 thread!\n"
        self.cond.notifyAll()
        self.cond.release()
        while True:
            try:
                req, arg, res = self.reqs.get()
            except:
                break;
            if TRACE_DB: print "run: ", req
            if req=='--close--': break
            try:
                self.cursor.execute(req, arg)
            except Exception, e:
                print Exception, e
                pass
            if res:
                for rec in self.cursor:
                    res.put(rec)
                res.put('--no more--')
    
    ## 线程版本，重载execute
    def execute(self, req, arg=None, res=None):
        if TRACE_DB: print "execSql: ", req 
        self.reqs.put((req, arg or tuple(), res))

    def selectSql(self, req, arg=None):
        ## 等线程创建了一个链接再说
        self.cond.acquire()
        if self.conn == None: self.cond.wait()
        self.cond.release()
        if TRACE_DB: print "enter selectSql\n" 
        res=Queue()
        self.execute(req, arg, res)
        while self.conn and True:
            rec=res.get()
            if rec=='--no more--': break
            yield rec
        if TRACE_DB: print "leave selectSql\n" 

    def close(self):
        self.execute('--close--')
        pass

    def execSql(self, sql):
        ## 等线程创建了一个链接再说
        if self.conn_failed : return None
        self.cond.acquire()
        if self.conn == None: self.cond.wait()
        self.cond.release()
        if self.conn: return self.execute(sql)
        else: return None

def sync_write(name):
    dbfile = '/tmp/testdbio'
    db = DBSQL(dbfile)
    table = 'tbl1'
    fields = [ ('f1', 'INTEGER'),
               ('f2', 'varchar(64)'), 
               ('f5', 'TIMESTAMP')
             ]
    if name:
        db.createTable(table, fields)
        name = 'master'
    else:
        name = 'slave'
    i = 1
    while i < 1000: 
        db.insert('tbl1', (i, name, getLocalTime()))
        time.sleep(1)
        i += 1
    db.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        arg = sys.argv[1]
    else:
        arg = None
    sync_write(arg)
