import os
from select import *
from socket import *


class WebServer:
    def __init__(self,host="0.0.0.0",port=80,html="./"):
        self.host=host
        self.port=port
        self.html=html
        self.create_socket()
        self.bind()
        self.rlist=[]
        self.wlist=[]
        self.xlist=[]
        self.file_list=os.listdir(self.html)
    #启动整个服务
    def start(self):
        self.sock.listen(5)
        self.rlist.append(self.sock)
        print("Listen the port %d"%self.port)

        #循环监控IO对象
        while True:
            rs,ws,xs=select(self.rlist,self.wlist,self.xlist)
            for r in rs:
                # 有客户端连接
                if r is self.sock:
                    connfd, addr = r.accept()
                    print("Connect from", addr)
                    # 将客户端连接套接字也监控起来
                    connfd.setblocking(False)
                    self.rlist.append(connfd)
                else:
                    # 处理浏览器发送的请求
                    self.handle(r)
                    self.rlist.remove(r)
                    r.close()

    def create_socket(self):
        self.sock=socket()
        self.sock.setblocking(False)

    def bind(self):
        self.addres=(self.host,self.port)
        self.sock.bind(self.addres)

    def handle(self,conn):
        request=conn.recv(1024*10).decode()
        print(request)
        if request:
            tmp=request.split(" ")[1]
            self.send_html(conn,tmp)

    def send_html(self,conn,tmp):
        if tmp in "/":
            with open(f"{self.html}/index.html","rb")as f:
                data=f.read()
                response = "HTTP/1.1 200 OK\r\nContent-Type:text/html\r\nContent-Length:%d\r\n\r\n"%len(data)
                response=response.encode()+data
                conn.send(response)
        elif tmp.replace("/","") in self.file_list:
            with open(f"{self.html}{tmp}","rb")as f:
                data = f.read()
                response = "HTTP/1.1 200 OK\r\nContent-Type:text/html\r\nContent-Length:%d\r\n\r\n"%len(data)
                response=response.encode()+data
                conn.send(response)
        else:
            with open(f"{self.html}/404.html","rb")as f:
                response = "HTTP/1.1 404 OK\r\nContent-Type:text/html\r\n\r\n".encode()
                response += f.read()
                conn.send(response)



if __name__ == '__main__':
    httpd=WebServer(host="0.0.0.0",port=8888,html="./static")
    httpd.start()


