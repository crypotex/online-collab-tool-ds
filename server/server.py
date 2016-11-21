import socket
import sys
import thread

class Server:
    def __init__(self):
        self.socket = self.socket_init("localhost")
        self.run()
        self.text = []

    def socket_init(self, server_ip):
        """ Socket Initialization """
        host = server_ip
        port = 49998
        backlog = 5
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(backlog)
        return s

    def run(self):
        while 1:
            client, accept = self.socket.accept()
            print("Incoming connection")
            print(client)
            print(accept)
            while 1:
                msg = client.recvfrom(1024)
                print(msg[0].split("*"))
                client.send(msg[0].split("*")[0])
                print(msg)

if __name__ == "__main__":
    srvr = Server()
    exit(0)
