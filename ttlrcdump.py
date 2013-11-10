# -*- coding: UTF-8 -*-
#auther mengskysama

import httplib2
import platform
import hashlib
import re

h = httplib2.Http(timeout=15)

def GetCiValue():
    return hashlib.md5(str(platform.uname())).hexdigest().upper()

def EncodeString2Hex(_str):
    ret = ''
    _str =  _str.decode('utf-8').encode('utf-16')[2:]
    for i in range(len(_str)):
        ret += '%02x' % ord(_str[i])
    return ret

def FilterSearchStr(_str):
    _str = _str.lower()
    _str = _str.replace(' ','')
    _str = _str.replace('&','')
    _str = _str.replace('>','')
    _str = _str.replace('<','')
    _str = _str.replace('?','')

    restrs = ('\(.*.\)', '\（.*.\）')
    for restr in restrs:
        p = re.compile(restr)
        res = p.findall(_str)
        for rep in res:
            _str = _str.replace(rep, '')

    return _str

def GetSearchLrcReq(artist, title):
    artist = FilterSearchStr(artist)
    title = FilterSearchStr(title)
    #print artist.decode('utf-8').encode('gbk')
    #print title.decode('utf-8').encode('gbk')
    return 'http://ttlrc.qianqian.com/dll/lyricsvr.dll?sh?Artist=%s&Title=%s&Flags=2&ci=%s' % (EncodeString2Hex(artist), EncodeString2Hex(title), GetCiValue())

def SearchLrc(artist, title):
    try:
        get_url = GetSearchLrcReq(artist, title)
        #print get_url
        head, ret = h.request(get_url)
    except IOError, e:
        print 'Search Requset Faild'
        if hasattr(e, 'code') and hasattr(e, 'reason'):
            print 'error code:%d - reason:%s.' % (e.code, e.reason)
        elif hasattr(e, 'code'):
            print "error code:%d" % e.code
        return ''
    return ret

def CodeEncrypt(id, artist, title):
    data = artist + title
    id = int(id)
    datalen = len(data)

    tmp2 = 0
    tmp1 = (id & 0x0000FF00) >> 8
    if ((id & 0x00FF0000) == 0 ):
        tmp3 = 0x000000FF & ~tmp1
    else:
        tmp3 = 0x000000FF & ((id & 0x00FF0000) >> 16)
    tmp3 = tmp3 | ((0x000000FF & id) << 8)
    tmp3 = tmp3 << 8
    tmp3 = tmp3 | (0x000000FF & tmp1)
    tmp3 = tmp3 << 8
    if ( (id & 0xFF000000) == 0 ) :
        tmp3 = tmp3 | (0x000000FF & (~id))
    else :
        tmp3 = tmp3 | (0x000000FF & (id >> 24))

    i = datalen - 1
    while(i >= 0):
        c = ord(data[i])
        if c >= 0x80:
            c = c - 0x100
        tmp1 = (c + tmp2) & 0x00000000FFFFFFFF
        tmp2 = (tmp2 << (i % 2 + 4)) & 0x00000000FFFFFFFF
        tmp2 = (tmp1 + tmp2) & 0x00000000FFFFFFFF
        i -= 1

    j = 0
    tmp1 = 0
    while(j <= datalen - 1):
        c = ord(data[j])
        if c >= 128:
            c = c - 256
        tmp4 = (c + tmp1) & 0x00000000FFFFFFFF
        tmp1 = (tmp1 << (j % 2 + 3)) & 0x00000000FFFFFFFF
        tmp1 = (tmp1 + tmp4) & 0x00000000FFFFFFFF
        j += 1

    tmp1 = ((((((tmp2 ^ tmp3) & 0x00000000FFFFFFFF) + (tmp1 | id)) & 0x00000000FFFFFFFF) * (tmp1 | tmp3)) & 0x00000000FFFFFFFF)  * (tmp2 ^ id) & 0x00000000FFFFFFFF

    if tmp1 > 0x80000000:
        tmp1 = tmp1 - 0x100000000

    return tmp1

def GetDownloadLrcReq(id, artist, title):
    return 'http://ttlrc.qianqian.com/dll/lyricsvr.dll?dl?Id=%s&Code=%s&ci=%s' % (id, CodeEncrypt(id, artist, title), GetCiValue())

def DownloadLrc(id, artist, title):
    try:
        get_url =  GetDownloadLrcReq(id, artist, title)
        #print get_url
        head, ret = h.request(get_url)
    except IOError, e:
        print 'DownloadLrc Requset Faild'
        if hasattr(e, 'code') and hasattr(e, 'reason'):
            print 'error code:%d - reason:%s.' % (e.code, e.reason)
        elif hasattr(e, 'code'):
            print "error code:%d" % e.code
        return ''
    return ret

def main():
    artist = '千反田える (佐藤聡美) & 伊原摩耶花 (茅野愛衣)'
    title = 'まどろみの約束♪'
    print SearchLrc(artist, title).decode('utf-8').encode('gbk')
    #szList = DownloadLrc('286735', '千反田える(佐藤聡美)&伊原摩耶花(茅野愛衣)[中日对照]', 'まどろみの約束')
    #print szList.decode('utf-8').encode('gbk')
if __name__ == '__main__':
    main()