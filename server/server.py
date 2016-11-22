import socket
from Protocol import ServerProtocol


TCP_RECIEVE_BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024
# Constants
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_PORT = 49995
DEFAULT_HOST = 'localhost'


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
                    msg = tcp_receive(client)
                    response = self.editor.handleEvent(msg)
                    client.sendall(response)
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


def tcp_send(sokk, data):
    """
    We don't close the socket.
    :param sokk: TCP socket; used to
    :param data: send all data
    :return: Int, number of bytes sent and error if any
    :throws: socket.error in case of transmission error
    """
    sokk.sendall(data)
    return len(data)


def tcp_receive(sokk):
    msg = ''
    while 1:
        block = sokk.recv(TCP_RECIEVE_BUFFER_SIZE)
        if len(block) <= 0:
            break
        if len(msg) + len(block) >= MAX_PDU_SIZE:
            sokk.shutdown(socket.SHUT_RD)
            del msg
            print("Deleted message because MAX PDU SIZE reached.")
        msg += block
    return msg


if __name__ == "__main__":
    srvr = Server()
    exit(0)
