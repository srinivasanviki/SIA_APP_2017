import socket
import time

MSGLEN=1048
class create_socket_client():
    def __init__(self):
        self.serversocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host=socket.gethostname()
        self.port=9999

    def connect(self):
        self.serversocket.connect((self.host,self.port))


    def receive(self):
        chunks = []

        chunk = self.serversocket.recv(MSGLEN)
        chunks.append(chunk)

        return ''.join(chunks)

    def recv_timeout(self,timeout=2):
        self.serversocket.setblocking(0)

        total_data=[];
        begin=time.time()
        while 1:
            if total_data and time.time()-begin > timeout:
                break
            elif time.time()-begin > timeout*2:
                break
            try:
                data = self.serversocket.recv(8192)
                if data:
                    total_data.append(data)
                    begin=time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        return ''.join(total_data)

def get_image_dimensions():
    cs=create_socket_client()
    cs.connect()
    msg=cs.recv_timeout()
    if msg:
        fh = open("/home/viki/sia_app_challenge/SIA_APP_2017/Python/image_to_analyse.jpg", "wb")
        fh.write(msg.decode('base64'))
        fh.close()
        from box_perspective import get_dimensions
        data= get_dimensions("/home/viki/sia_app_challenge/SIA_APP_2017/Python/image_to_analyse.jpg")
        return data
    cs.serversocket.close()





