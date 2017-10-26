import socket
import time

MSGLEN=2048
class create_socket():
    def __init__(self):
        self.serversocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host=socket.gethostname()
        self.port=9999

    def connect_socket(self):
        self.serversocket.bind((self.host,self.port))
        self.serversocket.listen(5)

    def send(self):
        from client import get_image_dimensions
        while True:
         msg=get_image_dimensions()
         print "Message is receiving You start sending to Port %s at Host %s"%(self.port,self.host)
         if msg:
             self.clientsocket,addr=self.serversocket.accept()
             self.clientsocket.sendall(msg)
             self.clientsocket.close()
             break


if __name__ == "__main__":
    cs=create_socket()
    cs.connect_socket()
    cs.send()

