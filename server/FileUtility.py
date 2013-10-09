#encoding=UTF-8
"""
xmgo prj, ver 0.0.2
FileUtility.py :  file utility
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


import os,sys
import struct
import tempfile
import shutil
import random
from   stat import *
import UnicodeUtil
from   misc import *
import pdb

def createFile(fileName, **kargs):
    """
       参数：
          fileName：文件名
          size：    初始文件大小，可选, 可以是50M, 100G, 10K等形式
          content:  文件内容，可选
          openmode: 打开模式, "r+b"--> update，"wb"--> new 
          offset:   从offset开始写
          return_file_object: 是否返回文件对象，可选，如果没指定则返回True
    """
    global BLOCK_SIZE
    def return_value(rfo, fp):
        if rfo:
            return fp 
        if fp == None: return False
        fp.close()
        return True
    content = getArg(kargs, 'content', None)
    openmode= getArg(kargs, 'openmode', None) 
    offset  = getArg(kargs, 'offset', 0) 
    size    = getArg(kargs, 'size', None) 
    return_file_object = getArg(kargs, 'return_file_object', False) 
    if  fileName == None: 
        return return_value( return_file_object, None )
    if size : 
        size = getFileSize(size)
        if size < 0: return return_value( return_file_object, None )
    try:
        if openmode == None: openmode = 'wb'
        fp = open(fileName, openmode)
        if size :
            fp.seek( size - 1, 0) ## create sparse file
            fp.write('\0')
        fp.seek(offset, 0)
        if content: fp.write(content)
    except Exception, e:
        fp = None
    return return_value( return_file_object, fp )

def closeFile(fp):
    if fp: fp.close()

def createDir(pathname, return_reason = False):
    def do_ret(ret, return_reason, reason):
        if return_reason:
            return (ret, reason)
        else:
            return ret
    reason = ""
    if  pathname == None: 
        return do_ret( False, return_reason, reason )
    try:
        os.makedirs(pathname)
        return do_ret( True, return_reason, reason )
    except Exception, e:
        return do_ret( False, return_reason, e)

def createPath(path):
    return createDir(path)

def deleteFile(file_list):
    if  file_list == None: return
    if isinstance(file_list, list) or isinstance(file_list, tuple):
        fl = file_list
    else:
        fl = [ file_list ]
    ret = True 
    for filename in fl:
        try:
            os.remove(filename) 
        except Exception, e:
            #print e
            ret = False
            pass
    return ret

def fileDelete(file_list):
    return deleteFile(file_list)

def deleteEmptyDir(pathname):
    try:
        os.rmdir(pathname) 
    except Exception, e:
        pass

def deleteDir(pathname):
    try:
        shutil.rmtree(pathname, True)
    except Exception, e:
        pass
    try:
        os.remove(pathname) 
    except Exception, e:
        pass

def deleteDirectory(pathname):
    return deleteDir(pathname)

def removePath(pathname):
    return deleteDir(pathname)


def pathExists(filename):
    if  filename == None: return False
    return os.path.exists(filename)

def dirExists(dirname):
    return pathExists(dirname)

def fileExists(pathname):
    if  pathname == None: return False
    return pathExists(pathname)

def fileLength(fn):
    if fn == None:
        return -1 
    try:
        st = os.lstat(fn)
    except :
        return -1
    return st[6]

def fileCopy(src_file, dest_file):
    """
        copy src_file to dest_file.
    """
    try:
        shutil.copyfile(src_file, dest_file) 
    except Exception, e:
        pass

def dirCopy(dir1, dir2, overwrite=True):
    """
       递归copy目录dir1 成 dir2, dir2如果存在的话，则缺省是覆盖。
    """
    try:
        if not pathExists(dir2):
            shutil.copytree(dir1, dir2) 
        else:
            path = dir1.rstrip("/")
            dest_path = dir2.rstrip("/")
            for p in os.listdir(path):
                if p == '.' or p == '..': continue
                src  = u"%s/%s" % (path, p)
                dest = u"%s/%s" % (dest_path, p)
                if isFile(src):
                    fileCopy(src, dest)
                else:
                    dirCopy(src, dest)
    except Exception, e:
        pass
   
def pathRename(oldName, newName):
    try:
        os.rename(oldName, newName)
    except Exception, e:
        pass

def fileRead(filename, **kargs):
    start = getArg(kargs, 'start', 0)
    size  = getArg(kargs, 'size', 0)
    try:
        fp = open(filename, "rb")
        if start != 0: f.seek(start, 0)
        if size > 0: 
            content = fp.read(size)
        else:
            content = fp.read() 
        fp.close() 
        return content
    except Exception, e:
        return None

def fileGeneratorRead(filename, **kargs):
    start = getArg(kargs, 'start', 0)
    size  = getArg(kargs, 'size', 0)
    if size <= 0: 
        yield fileRead(filename, **kargs)
    else:
        try:
            fp = open(filename, "rb")
            if start != 0: f.seek(start, 0)
            max_size = fileSize(filename)
            pos = start
            while pos < max_size: 
                if pos + size > max_size: 
                    size = max_size - pos
                yield fp.read(size)
                pos += size
            fp.close() 
        except Exception, e:
            pass

def fileWrite(filename, content, **kargs):
    start = getArg(kargs, 'start', 0)
    mode = getArg(kargs, 'mode', 'wb')
    try:
        fp = open(filename, mode)
        if start != 0: f.seek(start, 0)
        fp.write(content)
        fp.close() 
        return True 
    except Exception, e:
        return False 

def writeFile(filename, content):
    return fileWrite(filename, content)

def readFile(path):
    return fileRead(path)

def isFile(filename):
    return os.path.isfile(filename)

def isDirectory(filename):
    return os.path.isdir(filename)

def isDir(filename):
    return isDirectory(filename)

def isBlockDevice(filename):
    try:
        st = os.stat(filename)
        return S_ISBLK(st.st_mode)
    except Exception, e:
        return False 

def isDevice(filename):
    try:
        st = os.stat(filename)
        return st.st_rdev > 0
    except Exception, e:
        return False 

def fileMove(oldFile, newFile):
    try:
        shutil.move(oldFile, newFile)
        return True
    except Exception, e:
        print e
        return False
        pass

def fileSize(filename):
    """
        返回文件大小，单位：字节
    """
    return fileLength(filename)
    ##TODO
    fd= os.open(filename, os.O_RDONLY)
    size = 0
    try:
        size = os.lseek(fd, 0, os.SEEK_END)
    except Exception, e:
        size = 0
    finally:
        os.close(fd)
    return size


def listDir(path, just_directory = False, just_file = False):
    """
       列出指定目录path下的文件或目录列表。
       path: 全路径名
       just_directory = True: 只列出目录，否则也列出文件。
       just_file      = True: 只列出文件
    """
    path = path.strip()
    path_list = os.listdir(path)
    if just_directory == False: ## 列出目录和文件
        ret = []        
        for p in path_list:  ## 转成unicode
            try:
                full_path = u"%s%s%s" % (path, unicode(os.path.sep), UnicodeUtil.get_unicode_str(p))
            except Exception, e:
                continue
            if just_file: ## 只列文件
                if not isFile(full_path): ## 如果不是文件则排除
                    continue
            ret.append( UnicodeUtil.get_unicode_str(p) )
        return ret
        #return path_list
    if path.endswith(unicode(os.path.sep)) and len(path) > 1 :
        path = path.rstrip(unicode(os.path.sep))
    ret = []        
    for p in path_list:
        try:
            p = UnicodeUtil.get_unicode_str(p)
            full_path = u"%s%s%s" % (path, unicode(os.path.sep), p)
            if not pathExists( full_path ): continue
        except Exception, e:
            print e
            return [] 
        if isDirectory( full_path ): ret.append(p)
    return ret 

def listdir(path,  just_directory = False):   
    return listDir(path, just_directory)

def listfiles(path): ## 列出目录下所有文件，不包括目录
    return listDir(path, False, True)

def listAll(path, **kargs):
    """
      递归列出目录下所有文件/最后一级目录，内容中路径名不包括path
      just_directory = True: 只列出目录，否则列出文件。缺省为False
      contain_file   = True: 只列出包含文件的非空目录，与just_directory一起用, 缺省为False
      用yield方式返回
    """
    get_arg = lambda k, args, v: args[k] if k in args and args[k] != None else v
    just_directory = get_arg("just_directory", kargs, False)
    contain_file = get_arg("contain_file", kargs, False)
    path = os.path.normpath(path.strip())
    #pdb.set_trace()
    for root, dirs, files in os.walk(path):
        if just_directory:
            ok = False if contain_file and not files else True 
            if ok:
                pure_path = root.replace(path, "")
                yield pure_path 
            continue
        else:
            for fn in files:
                fp = os.path.join(root, fn.lstrip(os.path.sep))
                pure_path = fp.replace(path, "")
                yield pure_path 

def containSubDir(path):
    """
       判断指定路径是否包含子目录。
    """
    items = listdir(path, True)
    if len(items) > 0:
        return True 
    else:
        return False

def fileExt(path):
    base = os.path.basename(path)
    f1, ext = os.path.splitext(base)
    try:
        ext = ext.strip(".").lower()
        return ext
    except Exception, e:
        return ""

known_suffix = ['zip', 'tar', 'tgz', 'gzip', 'bz2', 'Z', 'arj', '7z', 'rar', 'cpio', 'gz']
def isArchiveFile(path):
    ext = fileExt(path)
    return  ext in known_suffix

user_perm  = [ S_IRUSR, S_IWUSR, S_IXUSR ]
group_perm = [ S_IRGRP, S_IWGRP, S_IXGRP ]
everybody_perm = [ S_IROTH, S_IWOTH, S_IXOTH ]

def fileMode(mode):
    perms = user_perm +  group_perm  + everybody_perm 
    i = 0
    for perm in perms:
        if '-' == perm: continue
        if 0 != (perm & mode):
            v = i % 3
            if v == 0  : perms[i] = 'r'
            elif v == 1: perms[i] = 'w'
            elif v == 2: perms[i] = 'x'
            else       : perms[i] = '-'
        else:
            perms[i] = '-'
        i = i+1
    return "".join(perms)

def fileOwner(uid):
    from pwd import getpwuid
    return getpwuid(uid).pw_name

def pathStripEndingSlash(path):    
    if path.endswith("/"):
        return path.rstrip("/")
    else:
        return path

def getCurDir():
    return os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))

if __name__ == '__main__':
    path = "./"
    for p in listAll(path): #, contain_file = True):
        print p
