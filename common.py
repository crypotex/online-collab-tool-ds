from socket import SHUT_RD


TCP_RECIEVE_BUFFER_SIZE = 1024*1024
MAX_PDU_SIZE = 200*1024*1024

# Constants
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_PORT = 49995
DEFAULT_HOST = 'localhost'

# Requests
__REQ_CHAR = '1' # Request for 1 character (insert, delete, etc)

# Responses
__RSP_OK = '0'

# Separator that separates tcp messages
__MSG_FIELD_SEP = '$'


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


def tcp_recieve(sokk):
    msg = ''
    while 1:
        block = sokk.recv(TCP_RECIEVE_BUFFER_SIZE)
        if len(block) <= 0:
            break
        if len(msg) + len(block) >= MAX_PDU_SIZE:
            sokk.shutdown(SHUT_RD)
            del msg
            print("Deleted message because MAX PDU SIZE reached.")
        msg += block
    return msg



