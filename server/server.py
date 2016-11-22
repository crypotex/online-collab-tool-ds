import sys
sys.path.append('..')
import socket
from Protocol import ServerProtocol
from common import DEFAULT_HOST, DEFAULT_PORT, tcp_recieve, tcp_send


class Server:
    def __init__(self):
        self.socket = self.socket_init(DEFAULT_HOST, DEFAULT_PORT)
        self.editor = ServerProtocol()
        self.run()

    def socket_init(self, server_ip, port):
        """ Socket Initialization """
        backlog = 5
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((server_ip, port))
            s.listen(backlog)
        except socket.error as e:
            print("Socket error: %s" % str(e))
            exit(1)
        return s

    def run(self):
        client = None
        while 1:
            try:
                client, source = self.socket.accept()
                print("Incoming connection: %s - %s" % (client, source))
                try:
                    msg = tcp_recieve(client)
                    response = self.editor.handleEvent(msg)
                    tcp_send(client, response)
                except socket.error as e:
                    print("Some error: %s" % (str(e)))

            except KeyboardInterrupt:
                print('Ctrl+C - terminating server')
                break

        if client is not None:
            try:
                client.close()
            except socket.error:
                print('Client disconnected')

        self.socket.close()
        print('Server socket closed.')



if __name__ == "__main__":
    srvr = Server()
    exit(0)
