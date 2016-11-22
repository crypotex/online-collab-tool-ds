import socket
from Protocol import ServerProtocol

class Server:
    def __init__(self):
        self.socket = self.socket_init("localhost", 49995)
        self.editor = ServerProtocol()
        self.run()

    def socket_init(self, server_ip, port):
        """ Socket Initialization """
        backlog = 5
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((server_ip, port))
        s.listen(backlog)
        return s

    def run(self):
        while 1:
            client, accept = self.socket.accept()
            print("Incoming connection")
            print(client)
            print(accept)
            while 1:
                msg, whaa = client.recvfrom(1024)
                response = self.editor.handleEvent(msg)
                client.send(response)
                print(msg)

if __name__ == "__main__":
    srvr = Server()
    exit(0)
