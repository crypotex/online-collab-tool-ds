import socket
import threading

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
        self.clients = []
        self.mainThreader()

    def socket_init(self, server_ip, port):
        """ Socket Initialization """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((server_ip, port))
        except socket.error as e:
            print("Socket error: %s" % str(e))
            exit(1)
        return s

    def mainThreader(self):
        self.socket.listen(5)
        while True:
            try:
                client, address = self.socket.accept()
                client.settimeout(7200)
                threading.Thread(target = self.runClientThread, args=(client, address)).start()
                self.clients.append((client,address))
                print(self.clients)
            except KeyboardInterrupt as kbe:
                print('Ctrl+C - terminating server')
                break
        self.socket.close()

    def runClientThread(self, client, address):
        print("New thread initialized with :%s and %s" % (client, address))
        while True:
            try:
                msg = client.recv(DEFAULT_BUFFER_SIZE)
                print("Recieved message: %s. Wwaiting for response." % msg)
                response = self.editor.handleEvent(msg)
                print("GODRESPONSE. Sending: %s." % response)
                client.send(response)
                print("SENTRESPO")
            except socket.error as e:
                print("Some error: %s" % (str(e)))
                break

        if client is not None:
            try:
                client.close()
            except socket.error:
                print('Client disconnected')



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


#Use only if working with some blocks of data
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
