# -*- coding: UTF-8 -*-
#auther mengskysama

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import lcs

from urllib import quote
from urllib import unquote
from tornado import gen

import ttlrcdump

listen_port = 38439

def ChooiseItem(xml, artist):
    #print '==============================================='
    #print xml.decode('utf-8').encode('gbk')

    n = xml.find('<?xml')
    if n == -1:
        return False

    artist = ttlrcdump.FilterSearchStr(artist)
    #remove item if artist != artist
    n = 0
    pos = 0
    t = xml.count('id=')
    for n in range(0, t):
        begin = xml.find('artist="', pos)
        end = xml.find('" title', begin)
        _artist = ttlrcdump.FilterSearchStr(xml[begin+8:end])
        pos = end
        n += 1
        arith = lcs.arithmetic()
        samelen = len(arith.lcs(_artist,artist))
        #print samelen
        if samelen < 5 and samelen < len(artist)/3 :
            begin = xml.rfind('<lrc',0 ,pos)
            end = xml.find('lrc>', pos)
            xml = xml[:begin] + xml[end + 4:]
            pos = begin
            n -= 1
            t -= 1

    #print xml.decode('utf-8').encode('gbk')
    #print '==============================================='
    n = xml.find('id=')
    if n == -1:
        return False

    #remove item if artist != artist
    n = 0
    begin = xml.find('artist="', n)
    end = xml.find('" title', n)
    n = end
    _artist = ttlrcdump.FilterSearchStr(xml[begin+10:end])

    strs =  ('动新','動新','动基','对照','對照','中日','中英','修正','假名')
    for _str in strs:
        n = xml.find(_str)
        if n != -1:
            break

    if n == -1:
        n = xml.find('<lrc')
    else:
        n = xml.rfind('<lrc', 0, n)

    if n > -1:
        begin = xml.find('id="', n) + 4
        end = xml.find('"', begin)
        #print xml[begin:end]
        id = xml[begin:end]

        begin = xml.find('artist="', n) + 8
        end = xml.find('"', begin )
        #print quote(xml[begin:end])
        artist = xml[begin:end].replace('&amp;','&').replace('&apos;',"'").replace('&quot;','"').replace('&lt;','<').replace('&gt;','>')

        begin = xml.find('title="', n) + 7
        end = xml.find('"', begin)
        #print quote(xml[begin + 7:end])
        title = xml[begin:end].replace('&amp;','&').replace('&apos;',"'").replace('&quot;','"').replace('&lt;','<').replace('&gt;','>')

        #ret = "id=%s&artist=%s&title=%s" % (id, quote(artist), quote(title))
        #print ret

        data = {'id':id, 'artist':artist, 'title':title}
        return data
    return False

def get_arg(req, arg):
    begin = req.find('%s=' % arg)
    if begin != -1:
        begin += len(arg) + 1
        end = req.find('&', begin)
        if end != -1:
            return req[begin:end]
        else:
            return req[begin:]

@gen.coroutine
def handle_request(request):

    if request.uri.startswith('/lrc'):
        id = get_arg(request.uri, 'id')
        artist = unquote(get_arg(request.uri, 'artist'))
        title = unquote(get_arg(request.uri, 'title'))
        #print id.decode('utf-8').encode('gbk')
        #print artist.decode('utf-8').encode('gbk')
        #print title.decode('utf-8').encode('gbk')
        try:
            http_client = tornado.httpclient.AsyncHTTPClient()
            #print ttlrcdump.GetDownloadLrcReq(id, artist, title)
            req = tornado.httpclient.HTTPRequest(ttlrcdump.GetDownloadLrcReq(id, artist, title))
            res = yield http_client.fetch(req)
            lrc = res.body.replace('>', '】')
            lrc = lrc.replace('<', '【')
            lrc = lrc.replace('\r\n', '<br />')
            lrc = lrc.replace('\n', '<br />')
            lrc = lrc.replace('\r', '<br />')
            context = '<script type="text/javascript" src="/templates/ddjs/lrc_content_inner_1.js"></script></div>%s</li>'
            context = context.replace('%s',lrc, 1)
            #print context
            request.write('HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s' % (len(context), context))
        except tornado.httpclient.HTTPError, code:
            print 'HTTPError except Code' + str(code)
        except Exception,e:
            print e
        finally:
            request.finish()


    elif (request.uri.find('/?keyword=') != -1):
        uri = request.uri.decode('gbk').replace('%20',' ')
        if uri.find('&') != -1:
            keyword = uri[10:uri.find('&')]
        else:keyword = uri[10:]

        #print repr(keyword)
        keyword = keyword.encode('gbk')
        #print repr(keyword)
        keyword = keyword.decode('utf-8')
        #print repr(keyword)
        keyword = eval(repr(keyword)[1:])
        #print repr(keyword)
        keyword = keyword.decode('gbk').encode('utf-8')
        #print keyword.decode('utf-8').encode('gbk')
        #print repr(keyword)

        try:
            if keyword.count(' ') == 0:
                keyword += ' '

            n = 0
            cnt = keyword.count(' ')
            for i in range(0, cnt):
                #try to prase art and title
                n = keyword.find(' ', n) + 1

                artist = keyword[0:n-1]
                title = keyword[n:]

                #print 'title %s' % title
                if title.startswith( '(') and i < cnt - 1:
                    #歌名一般不可能以括号开头
                    continue

                #print 'guess art=%s' % artist.decode('utf-8').encode('gbk')
                #print 'guess tit=%s' % title.decode('utf-8').encode('gbk')

                trycnt = 0
                while True:
                    reqartist = ''
                    reqtitle = ''
                    if trycnt == 0:
                        reqartist = artist.replace('and', '')
                        reqtitle = title.replace('and', '')
                    elif trycnt == 1:
                        reqartist = artist
                        reqtitle = title
                    elif trycnt == 2:
                        reqartist = artist.replace('and', '')
                        reqtitle = title
                    elif trycnt == 3:
                        reqartist = artist
                        reqtitle = title.replace('and', '')
                    http_client = tornado.httpclient.AsyncHTTPClient()
                    #print ttlrcdump.GetSearchLrcReq(artist, title)
                    req = tornado.httpclient.HTTPRequest(ttlrcdump.GetSearchLrcReq(reqartist, reqtitle))
                    res = yield http_client.fetch(req)
                    ret = ChooiseItem(res.body, artist)
                    trycnt += 1
                    if ret != False or trycnt > 3:
                        break

                if ret != False:
                    break

            if ret != False:
                context = '<div class="newscont mb15" style="line-height:160%;margin-top:10px">' \
                          '歌手:<a class="mr">%s</a><br>' \
                          '专辑:<a class="mr"></a>' \
                          '歌曲:<a class="mr ">%s<span class="highlighter">a</span></a><br>' \
                          '查看:<a class="mr"href="%s" target="_blank">LRC' \
                          '<div style="clear:both;"></div>' \
                          '<div class="page wid f14">'
                context = context.replace('%s', artist, 1)
                uni_title = title.decode('utf-8')
                strrep = ''
                for i in range(0, len(uni_title)):
                    strrep += '<span class="highlighter">%s</span>' % uni_title[i].encode('utf-8')
                context = context.replace('%s', strrep, 1)
                context = context.replace('%s', "/lrc/?id=%s&artist=%s&title=%s" % (str(ret['id']), quote(str(ret['artist'])), quote(str(ret['title']))))
                #print context.decode('utf-8').encode('gbk')
            else:
                context = 'Lrc Not Found'
            request.write('HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s' % (len(context), context))
        except tornado.httpclient.HTTPError, code:
            print 'HTTPError except Code' + str(code)
        except Exception,e:
            print e
        finally:
            request.finish()
    else:
        #print 'Unknow Request:%s' % request.uri
        context = '<head><meta http-equiv="refresh" content="0;url=http://foottlrc.mengsky.net/"></head>'
        request.write('HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n%s' % (len(context), context))
        request.finish()

def main():
    http_server = tornado.httpserver.HTTPServer(handle_request)
    http_server.listen(listen_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()