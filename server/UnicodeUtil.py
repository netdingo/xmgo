#coding=UTF-8
"""
xmgo prj, ver 0.0.2
UnicodeUtil.py: unicode utility
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


import encodings
import encodings.aliases
import encodings.utf_8
import encodings.utf_16
import encodings.ascii
import encodings.hex_codec
import encodings.gb2312
import encodings.gbk
import encodings.iso8859_1
import encodings.latin_1

## 注意：'utf_16' 和 'cp936'是同一种编码?
support_coding = ['ascii', 'utf_8', 'cp936', 'iso8859_1', 'unicode']
def get_encoding_type(s):
    """
       返回所指定字符串的编码类型及unicode编码，如果不在指定的编码范围，类型为'unknown'
       返回值: ( coding_type, unicode_string )
    """
    global support_coding
    if isinstance(s, unicode): ## 已经是Unicode
        return ('unicode', s)
    for a in support_coding:
        try:
            rv = s.decode(a)
            return (a, rv)
        except UnicodeEncodeError, e:
            pass
        except UnicodeDecodeError, e:
            ##print e 
            pass
    return ('unknown', s)

def get_specified_coding_string(s, coding_type):
    """
       返回指符串s指定类型coding_type的编码。
    """
    if isinstance(s, unicode): ## 已经是Unicode
        uni_str = s
    else:
        ct, uni_str = get_encoding_type(s)
        if ct == 'unknown':
            raise UnicodeDecodeError
            return s ## 不知道的编码类型
        if ct == coding_type:
            return s
    if coding_type == 'unicode':  ##如果所要求的是unicode的话，不用转换
        return uni_str
    else:
        return uni_str.encode(coding_type)

def get_utf8_str(s):
    return get_specified_coding_string(s, 'utf_8')

def get_unicode_str(s):
    return get_specified_coding_string(s, 'unicode')

def get_ascii_str(s):
    return get_specified_coding_string(s, 'ascii')

def param_coding_converter(param, codeType, convert_key = True):    
    if isinstance(param, unicode) or isinstance(param, str):
        return  get_specified_coding_string(param, codeType)
    elif isinstance(param, int) or isinstance(param, bool):
        return param
    elif isinstance(param, list) or isinstance(param, tuple):
        val = []
        for item in param:
            val.append(param_coding_converter(item, codeType, convert_key))
    elif isinstance(param, dict):
        val = {}
        for key, value in param.items():
            if convert_key : key = param_coding_converter(key, codeType, convert_key)
            val[key] = param_coding_converter(value, codeType, convert_key)
    else:
        val = param
    return val            

def convert_param_to_unicode(param, convert_key = True):
    """
        转化有的参数成为unicode.
        参数: param: 要转换的值
              convert_key: 只对dict参数起作用，
                  True: 也转换dict的key, 缺省也转换key
                  False:不转换dict的key 
    """
    return param_coding_converter(param, 'unicode', convert_key)

def convert_param_to_utf8(param, convert_key = True):
    """
        转化有的参数成为utf_8.
        参数: param: 要转换的值
              convert_key: 只对dict参数起作用，
                  True: 也转换dict的key, 缺省也转换key
                  False:不转换dict的key 
    """
    return param_coding_converter(param, 'utf_8', convert_key)

""" dump any string to formatted hex output """
def dump(s):
    import types
    if type(s) == types.StringType:
        return dumpString(s)
    elif type(s) == types.UnicodeType:        
        return dumpUnicodeString(s)

FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])

""" dump any string, ascii or encoded, to formatted hex output """
def dumpString(src, length=16):
    result = []
    for i in xrange(0, len(src), length):
       chars = src[i:i+length]
       hex = ' '.join(["%02x" % ord(x) for x in chars])
       printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
       result.append("%04x  %-*s  %s\n" % (i, length*3, hex, printable))
    return ''.join(result)

""" dump unicode string to formatted hex output """
def dumpUnicodeString(src, length=8):
    result = []
    for i in xrange(0, len(src), length):
       unichars = src[i:i+length]
       hex = ' '.join(["%04x" % ord(x) for x in unichars])
       printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in unichars])
       result.append("%04x  %-*s  %s\n" % (i*2, length*5, hex, printable))
    return ''.join(result)

""" read unicode string from encoded file """
def readFile(path, encoding, errors="replace"):
    raw = open(path, 'rb').read()
    uniText = raw.decode(encoding, errors)
    return uniText

""" write unicode string to encoded file """
def writeFile(path, uniText, encoding, errors="replace"):
    encText = uniText.encode(encoding, errors)
    open(path, 'wb').write(encText)
    
_norm_encoding_map = ('                                              . '
                      '0123456789       ABCDEFGHIJKLMNOPQRSTUVWXYZ     '
                      ' abcdefghijklmnopqrstuvwxyz                     '
                      '                                                '
                      '                                                '
                      '                ')
def test_encoding():
    import types
    encoding = "ISO-8859-1"
    if hasattr(types, "UnicodeType") and type(encoding) is types.UnicodeType:
        encoding = encoding.encode('latin-1')
    new_encodings = '_'.join(encoding.translate(_norm_encoding_map).split())
    print new_encodings

if __name__ == "__main__":
    test_encoding()

