import socket
from time import sleep

host = "localhost"
port = 51936

def listen(host, port):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(10)
        print("Server is listening at %s:%s" % (host, port))
        while True:
            conn, addr = s.accept()
            with conn:
                # https://stackoverflow.com/questions/383738/104-connection-reset-by-peer-socket-error-or-when-does-closing-a-socket-resu
                sleep(0.01)
                received_msg = ""
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    received_msg += data.decode("utf-8")
                    conn.sendall(b"Message received")  # これいる？
                print(received_msg)


if __name__ == '__main__':
    listen(host, port)
