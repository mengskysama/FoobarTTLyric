FoobarTTLyric
=============

Foobar Lyrics Show Pannel 3 下载千千静听(百度播放器)歌词库

Foobar TT Lrc Down (foottlrc) replace source www.lrc123.com to download lyric by Foobar tool Lyrics Show Pannel 3.

foottlrc result number is more than Timestamped3.

Notice: foottlrc always return contain Chinese Lyric (if has).Sure you can change it and run in yourself server.

=============
How to use it

1.see hack version foo_uie_lyrics3 http://tt.mengsky.net/

=============
How to build server

1.you must have public ip listen at 80

2.install python and lib we need

3.you can edit listen_port = 80 or use Reverse Proxy like this

server {
	listen       80;
	location / {
		resolver     8.8.8.8;
		proxy_pass http://127.0.0.1:38439$request_uri;
	}
}

4.Run it 'python lrcserv.py'
