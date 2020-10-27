from select import *
from socket import socket

#xxxxxxx
class EpollServer:
    def __init__(self,host="0.0.0.0",port=8888,url="./"):
        self.host=host
        self.port=port
        self.url=url
        self.start_sock()
        self.bind()
        self.ep=epoll()
        self.user={}
    def start_sock(self):
        """
        创建套接字
        :return:
        """
        self.sock=socket()
        self.sock.setblocking(False)

    def bind(self):
        """
        绑定地址
        :return:
        """
        addr=(self.host,self.port)
        self.sock.bind(addr)

    def run(self):
        self.sock.listen(5)
        self.user[self.sock.fileno()]=self.sock
        self.ep.register(self.sock,EPOLLIN)
        while True:
            even=self.ep.poll()
            for fd,type in even:
                if fd==self.sock.fileno():
                    conn,addr=self.user[fd].accept()
                    conn.setblocking(False)
                    self.ep.register(conn,EPOLLIN)
                    self.user[conn.fileno()]=conn
                else:

                    self.handle(self.user[fd])
                    self.ep.unregister(fd) # 不再关注
                    self.user[fd].close()
                    del self.user[fd] # 从字典删除


    def handle(self,conn):
        """
        接收客户端发送的请求
        :param conn: 客户端连接套接字
        :return:
        """
        data=conn.recv(1024*10).decode()
        print(data)
        if data:
            tmp=data.split(" ")[1]

            self.send_html(conn,tmp)

    def send_html(self,fd,tmp):
        """
        判断客户端的请求
        :param fd: 客户端连接套接字
        :param tmp: 客户端请求内容
        :return:
        """

        if tmp=="/":
           filename=self.url+"/index.html"
        else:
           filename=self.url+tmp
        try:
           f=open(filename,"rb")
        except:
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            filename=self.url+"/404.html"
            with open(filename,"rb")as f:
                data=f.read()
                response=response.encode()+data
                fd.send(response)
        else:
            response = "HTTP/1.1 200 OK Found\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response=response.encode()+f.read()
            fd.send(response)

if __name__ == '__main__':
    p=EpollServer(host="0.0.0.0",port=8888,url="./static")
    p.run()