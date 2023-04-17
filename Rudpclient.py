import os
import random
import string
import struct
import socket
import time

serverPort = 67
clientPort = 68
rudp_client_port = 20700
rudp_server_port = 30700
MAX_RECV_BYTES = 65535
MAX_SEND_BYTES = 32768
dnsport = 53
IP = socket.gethostbyname(socket.gethostname())

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class RUDPClient:

    def __init__(self):
        self.IPADDR = ""
        self.SUBNETMUSK = ""
        self.DEFULTGATEWAY = ""
        self.server_ip_address = ""
        self.client_ip_address = ""
        self.domain_name = "FileTransfer-M&S"
        self.average_RTT_delay = 2

    def client(self):
        print("DHCP client is starting...\n")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('0.0.0.0', clientPort))

        # DHCP request
        while self.IPADDR == "" or self.SUBNETMUSK == "" or self.DEFULTGATEWAY == "":
            self.DHCP_communication(s)

        # DNS request
        while self.server_ip_address == "":
            self.DNS_communication(s)

        while 1:
            print("\nEnter 1 if you want to upload a file ")
            print("Enter 2 if you want to download a file ")
            print("Enter 3 if you want to see all files ")
            print("Enter 4 if you want to remove a file")
            print("Enter 5 if you want a good movie recommendation")
            choice3 = input("Enter 6 if you want to exit ")
            if choice3 == "1":
                print("Hello user ,You chose to work with upload")
                org_filename = input("Please enter name of the file you want to upload ")
                new_filename = input("Please enter name of the new file")
                if org_filename == new_filename:
                    print("sorry, you must call the files in different names")
                    continue
                self.upload_request(org_filename, new_filename)
                time.sleep(2)

            elif choice3 == "2":
                print("Hello user ,You chose to work with download\n")
                org_filename = input("Please enter name of the file you want to download\n")
                files_list = self.show_files_request()
                if org_filename not in files_list:
                    print("sorry, the file you wish to download doesn't exist")
                    continue
                new_filename = input("Please enter name of the new file\n")
                self.download_request(org_filename, new_filename)
                time.sleep(2)

            elif choice3 == "3":
                print("Hello user ,You choose to work with Show_files ")
                files_list = self.show_files_request()
                print(files_list)
                time.sleep(2)

            elif choice3 == "4":
                files_list = self.show_files_request()
                org_filename = input("Please enter name of the file you want to remove\n")
                if org_filename not in files_list:
                    print("sorry, the file you wish to delete doesn't exist")
                    continue
                y1, y2, y3 = "N", "N", "N"
                y1 = input("are you sure you want to delete the file? Y/N")
                if y1 == "N": continue
                y2 = input("there is no way back.. u know, insert Y/N")
                if y2 == "N": continue
                y3 = input("are you really sure that you want to delete? Y/N")
                if y3 == "N": continue

                ans = self.remove_file(org_filename)
                if ans == -1:
                    print("sorry, there is a problem with connecting to the server, please try again")
                    continue

            elif choice3 == "5":
                print("always here for you <3")
                self.movies_recommendations()

            elif choice3 == "6":
                print("bye bye ")
                s.close()
                return

    def DNS_communication(self, s: socket):
        try:
            dest = ('<broadcast>', dnsport)
            s.sendto(self.domain_name.encode(), dest)
            packet, address = s.recvfrom(MAX_RECV_BYTES)
            self.server_ip_address = packet.decode("ascii")
        except:
            return

    def DHCP_communication(self, s: socket):
        try:
            OIPADDR = ""
            print("sending DHCP discovery...")
            dest = ('<broadcast>', serverPort)
            packet, TID = self.pack_discover()
            s.sendto(packet, dest)
            packet, address = s.recvfrom(MAX_RECV_BYTES)
            print("received DHCP offer")
            OIPADDR = self.unpack_offer(packet, TID)
            print("sending DHCP request...")
            dest = (address[0], serverPort)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            data = self.pack_request(OIPADDR, TID)
            s.sendto(data, dest)
            data, address = s.recvfrom(MAX_RECV_BYTES)
            self.unpack_ack(data, TID)
            print("received DHCP ack\n")
        except:
            pass

    def movies_recommendations(self):
        movies_rec = ["Maniac (1934)", "Reefer Madness (1936)", "The Terror of Tiny Town (1938)",
                      "The Babe Ruth Story (1948)"
            , "365 Days (2020)", "Cats (2019)", "Loqueesha (2019)", "Guardians (2017)", "Dirty Grandpa (2016)",
                      "United Passions (2014)"]
        num = random.randint(1, 10)
        print(movies_rec[num])
        print("believe me, it's the best")

    def show_files_request(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', rudp_client_port))
        dest = (IP, rudp_server_port)
        excepted_sequence_num, request_type, file_size = 1, 2, 1
        padded_file_name = "blabla"
        packet = struct.pack("h 50s h i", request_type,
                             padded_file_name.encode("ascii"), excepted_sequence_num, file_size)
        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type != 18:
            print("failed to access server")
            return
        self.download_request("serverfilelist.txt", "clientfilelist.txt")
        with open("clientfilelist.txt", "r") as file:
            a = file.read()
            list_files = a.split(', ')
        return list_files

    def pack_discover(self):
        PTYPE = "0"
        TID = get_random_string(8)
        packet = struct.pack("s 8s", PTYPE.encode("ascii"), TID.encode("ascii"))
        return packet, TID

    def unpack_offer(self, packet, TID):
        PTYPE, tid, OIPADDR, ODFLTGTWY, OSBNTMSK, LEASETIME = struct.unpack("s 8s i 11s 13s i", packet)
        if tid.decode() != TID:
            print("FRAUD!!!")
            exit(-1)
        if PTYPE.decode("ascii") != "3":
            print("wrong address")
            exit(-1)
        self.IPADDR = "10.0.0." + str(OIPADDR)
        self.SUBNETMUSK = OSBNTMSK.decode("ascii")
        self.DEFULTGATEWAY = ODFLTGTWY.decode("ascii")
        return OIPADDR

    def pack_request(self, ipaddr, TID):
        PTYPE = "4"
        packet = struct.pack("s 8s i", PTYPE.encode("ascii"), TID.encode("ascii"), ipaddr)
        return packet

    def unpack_ack(self, packet, TID):
        PTYPE, tid = struct.unpack("s 8s", packet)
        if tid.decode() != TID:
            print("FRAUD!!!")
            exit(-1)
        if PTYPE.decode("ascii") != "7" and PTYPE.decode("ascii") != "9":
            print("wrong address")
            exit(-1)
        if PTYPE.decode("ascii") == "9":
            print("sorry, server has reached full capacity, please try again later")
            self.IPADDR = ""
            self.SUBNETMUSK = ""
            self.DEFULTGATEWAY = ""
            return
        else:
            print("got IP address and ready to start communicate :)")

    # RUDP:

    def remove_file(self, file_name):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(False)
        s.bind(('', rudp_client_port))
        dest = (IP, rudp_server_port)

        padded_file_name = file_name.ljust(50, "0")
        excepted_sequence_num, request_type, file_size = 0, 3, 0
        packet = struct.pack("h 50s h i", request_type,
                             padded_file_name.encode("ascii"), excepted_sequence_num, file_size)
        s.sendto(packet, dest)
        time1 = time.time()
        while time.time() <= time1 + self.average_RTT_delay:
            try:
                ack, address = s.recvfrom(MAX_RECV_BYTES)
                ack_type, excepted_sequence_num = struct.unpack("2h", ack)
                if ack_type != 19:
                    print("problem with connecting the server")
                    return -1
            except:
                pass
            finally:
                s.close()

    def download_request(self, file_name, new_file_name):
        packet = None
        defult_chunk_size, chunk_size = 2048, 2048
        last_seq_num, num_of_dups = 0, 0
        RTT = []
        partial_RTT = []

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', rudp_client_port))
        dest = (IP, rudp_server_port)

        padded_file_name = file_name.ljust(50, "0")
        excepted_sequence_num, request_type, file_size = 1, 1, 1
        packet = struct.pack("h 50s h i", request_type,
                             padded_file_name.encode("ascii"), excepted_sequence_num, file_size)
        s.sendto(packet, dest)
        data = None
        try:
            data, address = s.recvfrom(MAX_RECV_BYTES)
        except:
            pass
        s.setblocking(False)
        excepted_request_type = struct.unpack_from("h", data, 0)
        if excepted_request_type == 200:
            print("file doesn't exist")
            return
        try:
            file = open(new_file_name, "wb+")
        except:
            raise

        while 1:
            current_time = time.time()
            while time.time() <= current_time + self.average_RTT_delay:
                try:
                    packet = None
                    packet, address = s.recvfrom(MAX_RECV_BYTES)
                except:
                    continue
                # calculating average RTT
                RTT_time = time.time()
                if len(partial_RTT) == 2:
                    RTT_delay = partial_RTT[1] - partial_RTT[0]
                    partial_RTT = []
                    if RTT_delay > 0:
                        RTT.append(RTT_delay)
                    sum = 0
                    for i in RTT:
                        sum += i
                    self.average_RTT_delay = 2 + (sum / len(RTT))
                else:
                    partial_RTT.append(RTT_time)
                if len(packet) < struct.calcsize("2h i " + str(chunk_size) + "s"):
                    break
                if packet is not None:
                    # print("chunksize: " + str(chunk_size))
                    # print("calcsize: " + str(struct.calcsize("2h i " + str(chunk_size) + "s")))
                    request_type, excepted_sequence_num, data_length, file_data \
                        = struct.unpack("2h i " + str(chunk_size) + "s", packet)
                    if request_type != 21 and request_type != -3:
                        print("FRAUD!!!")
                        return
                    file.write(file_data[:data_length])
                    last_seq_num = excepted_sequence_num
                    if chunk_size < MAX_SEND_BYTES: chunk_size *= 2
                    excepted_sequence_num += 1
                    if request_type == -3:
                        self.send_ack(excepted_sequence_num, s, dest, ack_type=17)
                        break
                    self.send_ack(excepted_sequence_num, s, dest)
            if request_type == -3: break
            self.send_ack(last_seq_num, s, dest)
            num_of_dups += 1
            if num_of_dups == 2:
                if chunk_size < MAX_SEND_BYTES: chunk_size = int(chunk_size * 1.2)
            if num_of_dups == 3:
                chunk_size = defult_chunk_size
                num_of_dups = 0
        s.setblocking(True)
        file.close()
        print("finished a download request: ")
        print("file name: " + file_name + " finished downloading.")
        print("file: " + new_file_name + " is ready to use")
        print("average RTT = " + str(self.average_RTT_delay))
        file.close()
        return

    def send_ack(self, last_seq_num: int, s: socket, dest, ack_type=16):
        packet = struct.pack("2h", ack_type, last_seq_num)
        s.sendto(packet, dest)

    def upload_request(self, file_name, new_file_name):
        padded_file_name = new_file_name.ljust(50, "0")
        defult_chunk_size, chunk_size = 2048, 2048
        dup_ack_counter, recent_ack_packet_num = 0, 0
        current_read, excepted_sequence_num, request_type, flag = 0, 0, 0, 0
        try:
            filed = open(file_name, "rb")
        except:
            raise

        filed.seek(0, os.SEEK_END)
        file_size = filed.tell()
        filed.seek(0, os.SEEK_SET)
        List = []

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', rudp_client_port))
        dest = (self.server_ip_address, rudp_server_port)

        packet = struct.pack("h 50s h i", request_type,
                             padded_file_name.encode("ascii"), excepted_sequence_num, file_size)
        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type != 16:
            print("FRAUD!!!!")
            return
        recent_ack_packet_num = excepted_sequence_num

        while current_read + chunk_size <= file_size:
            excepted_sequence_num += 1
            List.append((excepted_sequence_num, current_read, current_read + chunk_size))
            current_read += chunk_size
            request_type = 0
            data_length = chunk_size
            packet = struct.pack("h h i " + str(chunk_size) + "s", request_type, excepted_sequence_num,
                                 data_length, filed.read(chunk_size))  # .encode("ascii")
            s.sendto(packet, dest)
            ack, address = s.recvfrom(MAX_RECV_BYTES)
            ack_type, excepted_sequence_num = struct.unpack("2h", ack)
            if ack_type != 16:
                print("FRAUD!!!!")
                return
            if excepted_sequence_num == recent_ack_packet_num:
                dup_ack_counter += 1
                if dup_ack_counter == 2:
                    if chunk_size < MAX_SEND_BYTES: chunk_size = int(chunk_size * 1.2)
                if dup_ack_counter > 2:
                    print("startover")
                    chunk_size = defult_chunk_size
                for i in List:
                    if i[0] > recent_ack_packet_num:
                        List.remove(i)
                current_read = List[len(List) - 1][2]
                excepted_sequence_num = recent_ack_packet_num
            else:
                recent_ack_packet_num = excepted_sequence_num
                dup_ack_counter = 0
                if chunk_size < MAX_SEND_BYTES: chunk_size *= 2
        excepted_sequence_num += 1
        request_type = -3
        data_length = file_size - current_read
        packet = struct.pack("h h i " + str(chunk_size) + "s", request_type, excepted_sequence_num,
                             data_length, filed.read(chunk_size))  # .encode("ascii")
        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type == 17:
            print("finished with: " + str(address[0]))
        filed.close()
        return


if __name__ == '__main__':
    rudp_client = RUDPClient()
    rudp_client.client()
