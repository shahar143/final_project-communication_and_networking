import socket
import threading

SIZE = 2048


def to_stop_or_not_to_stop(thread):
    choice2 = ""
    while 1:
        choice = input("do you want to pause the process? Y/N")
        if choice == "Y":
            thread.wait()
            while choice2 != "C":
                choice2 = input("insert the letter C when you want to continue the process")
            thread.notify()
            choice2 = ""


class stopper_thread:
    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        dest = ("127.0.0.1", 20334)
        server.bind(dest)
        server.listen()
        print("listening...")

        client_socket, client_address = server.accept()
        request_client = int(client_socket.recv(SIZE).decode("ascii"))

        thread = threading.Thread(target=to_stop_or_not_to_stop(request_client))
        thread.start()


if __name__ == '__main__':
    stopper_thread1 = stopper_thread()
    stopper_thread1.server()
