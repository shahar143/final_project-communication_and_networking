import threading
import time
import socket

from Rudpclient import RUDPClient


class Guardthread:
    state = None

    def __init__(self):
        self.users_list = {"shahar": "aaaaaa"}

    def file_transfer_app(self):
        thread = threading.Thread(target=self.guard_thread_act())
        dest = ("127.0.0.1", 20334)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(dest)
        thread.start()
        request = str(thread.ident).encode("ascii")
        if request is not None:
            client.send(request)
        else:
            print("shit")
        print("message sent")

    def guard_thread_act(self):
        state = threading.current_thread()
        rudp_client = RUDPClient()
        while 1:
            if self.sign_in():
                rudp_client.client()
            else:
                exit(-1)

    def sign_in(self):
        counter = 0
        user = input("please insert user name: ")
        while user not in self.users_list.keys() or len(self.users_list) == 0:
            if counter < 2:
                print("username doesn't exist. please check for typo errors or register if you haven't registered yet")
                choice = input("if you would like to register, insert 1: ")
                if int(choice) == 1:
                    self.register()
                    print("almost done! please sign in again ")
                    break
                else:
                    user = input("please insert user name: ")
            elif 2 < counter < 6:
                print("listen buddy I don't have all day. please check for typo errors or register "
                      "if you haven't registered yet")
                choice = input("if you would like to register, insert 1: ")
                if int(choice) == 1:
                    self.register()
                    break
                else:
                    user = input("please insert user name: ")
            elif counter > 6:
                print("that's enough, bye bye")
                exit(-1)
            counter += 1
        password = input("please insert your password: ")
        counter = 0
        while self.users_list[user] != password:
            if counter < 3:
                print("wrong password, please try again")
                password = input("please insert your password: ")
            elif counter == 4:
                print("the app is currently blocked for 30 seconds due to unsuccessful attempts")
                time.sleep(3)
                print("just kidding, we are not these kind of guys")
                input1 = input("insert 6 to reset your password ")
                if input1 == "6":
                    self.change_password(user)
                password = input("please insert your password: ")
            elif counter > 5:
                print("INTRUDER!!!! FRAUD!!!!!! HORROR!!!! bye")
                exit(-1)
            counter += 1
        return True

    def register(self):
        username = input("please insert a username, from 3 up to 20 characters long")
        username.rstrip(" ")
        while 1:
            if username in self.users_list.keys():
                print("user name already exist, please choose a different name")
                username = input("please insert a username, up to 20 characters long")
            elif len(username) < 3 or len(username) > 20:
                username = input("please insert a username, up to 20 characters long")
            else:
                break

        password = input("Please enter a password between 8-14 characters, it must contain a capital letter, a lower "
                         "case letter, a number, a special character, a punctuation sign, a dragon egg, a tooth of a "
                         "basilisk, the 15467th digit of pi, my grade in reshatot and Captain Americas favorite color")
        while 1:
            if len(password) < 6 or len(password) > 14:
                password = input("please insert password in length between 6 and 14 characters long")
            else:
                break

        self.users_list.update({username: password})

    def change_password(self, username):
        if username not in self.users_list.keys():
            print("error")
            return -1

        password = input("Please enter a password between 8-14 characters, it must contain a capital letter, a lower "
                         "case letter, a number, a special character, a punctuation sign, a dragon egg, a tooth of a "
                         "basilisk, the 15467th digit of pi, my grade in reshatot and Captain Americas favorite color")
        while 1:
            if len(password) < 6 or len(password) > 14:
                password = input("please insert password in length between 6 and 14 characters long")
            else:
                break

        self.users_list[username] = password


if __name__ == '__main__':
    guardthread = Guardthread()
    guardthread.file_transfer_app()
