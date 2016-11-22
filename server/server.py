import socket
import threading
import logging

from Protocol import ServerProtocol


TCP_RECIEVE_BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024
# Constants
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_PORT = 49995
DEFAULT_HOST = 'localhost'

FORMAT = '%(asctime)-15s %(levelname)s %(threadName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger()


class Server:
    def __init__(self):
        LOG.info("Server Started.")
        self.socket = self.__socket_init(DEFAULT_HOST, DEFAULT_PORT)
        self.editor = ServerProtocol()
        self.clients = []
        self.main_threader()

    @staticmethod
    def __socket_init(server_ip, port):
        """ Socket Initialization """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((server_ip, port))
        except socket.error as e:
            LOG.error("Socket error: %s" % str(e))
            exit(1)
        LOG.info("Socket initialized")
        return s

    def main_threader(self):
        self.socket.listen(5)
        while True:
            try:
                client, address = self.socket.accept()
                client.settimeout(7200)
                threading.Thread(target=self.run_client_thread, args=(client, address)).start()
                self.clients.append((client, address))
                LOG.info("Current Clients: %s" % str(self.clients))
            except KeyboardInterrupt:
                LOG.exception('Ctrl+C - terminating server')
                break
        self.socket.close()

    def run_client_thread(self, client, address):
        LOG.info("New thread initialized with :%s and %s" % (str(client), address))
        while True:
            try:
                msg = client.recv(DEFAULT_BUFFER_SIZE)
                if len(msg) == 0:
                    break
                LOG.debug("Recieved message from client %s. Message was: %s." % (address, msg))
                response = self.editor.handleEvent(msg)
                LOG.debug("Sending response: %s to client %s." % (response, address))
                client.send(response)
                LOG.debug("Response GODSENT.")
            except socket.error as e:
                LOG.error("Some error: %s" % (str(e)))
                break

        if client is not None:
            try:
                client.close()
            except socket.error:
                LOG.info("Client %s disconnected." % address)


# Use only if working with some blocks of data
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
