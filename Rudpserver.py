import os
import pickle
import socket
import struct
import time

server_port = 30700
client_port = 20700
MAX_RECV_BYTES = 65535
MAX_SEND_BYTES = 32768


class RUDPServer:

    def __init__(self):
        self.files_list = []
        self.users_list = {}

    def server(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', server_port))
        print("Rudpserver waiting for connections")
        while 1:
            try:
                data, address = s.recvfrom(MAX_RECV_BYTES)
                dest = (address[0], client_port)
                request_type, padded_file_name, excepted_sequence_num, \
                    data_length = struct.unpack("h 50s h i", data)
                if request_type == 0:
                    print("hello client I will upload to you the file , in milliseconds")
                    self.accept_upload_request(data, s, dest)
                if request_type == 1:
                    print("hello client I will download to you the file , in milliseconds")
                    self.accept_download_request(data, s, dest)
                if request_type == 2:
                    print("hello client I will sent to you the files , in milliseconds")
                    self.accept_show_files_request(s, dest)
                if request_type == 3:
                    self.accept_remove_file_request(data, s, dest)
            except:
                raise

    def accept_remove_file_request(self, packet, s, dest):
        request_type, padded_file_name, excepted_sequence_num, \
            data_length = struct.unpack("h 50s h i", packet)
        file_name = str(padded_file_name.decode("ascii")).rstrip("0")
        os.remove(file_name)
        self.files_list.remove(file_name)
        self.send_ack(0, s, dest, ack_type=19)

    def accept_show_files_request(self, s: socket, dest):
        try:
            file = open("serverfilelist.txt", "w+")
        except:
            raise
        file.write(', '.join(self.files_list))
        self.send_ack(0, s, dest, ack_type=18)

    def accept_upload_request(self, first_packet, s: socket, dest):
        request_type, excepted_sequence_num, data_length, file_data = "", 0, 0, ""
        s.setblocking(0)
        defult_chunk_size, chunk_size = 2048, 2048
        last_seq_num, num_of_dups = 0, 0
        RTT = []
        partial_RTT = []
        average_RTT_delay = 2
        request_type, padded_file_name, excepted_sequence_num, \
            data_length = struct.unpack("h 50s h i", first_packet)
        file_name = str(padded_file_name.decode("ascii")).rstrip("0")
        print("new file: " + file_name)
        self.files_list.append(file_name)
        try:
            file = open(file_name, "wb+")
        except:
            raise
        excepted_sequence_num += 1
        self.send_ack(excepted_sequence_num, s, dest)
        # if chunk_size < MAX_SEND_BYTES:
        #     chunk_size *= 2
        while 1:
            current_time = time.time()
            while time.time() <= current_time + average_RTT_delay:
                try:
                    packet = None
                    packet, address = s.recvfrom(MAX_RECV_BYTES)
                except:
                    continue
                # if len(packet) < struct.calcsize("2h i " + str(chunk_size) + "s"):
                #     break
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
                    average_RTT_delay = 2 + (sum / len(RTT))
                else:
                    partial_RTT.append(RTT_time)
                if packet is not None:
                    # print("chunksize: " + str(chunk_size))
                    # print("calcsize: " + str(struct.calcsize("2h i " + str(chunk_size) + "s")))
                    try:
                        request_type, excepted_sequence_num, data_length, file_data \
                            = struct.unpack("2h i " + str(chunk_size) + "s", packet)
                    except:
                        continue
                    if request_type != 0 and request_type != -3:
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
        print("finished an upload request: ")
        print("file name: " + file_name + " finished uploading.")
        print("average RTT = " + str(average_RTT_delay))
        file.close()
        return

    def send_ack(self, last_seq_num: int, s: socket, dest, ack_type=16):
        packet = struct.pack("2h", ack_type, last_seq_num)
        s.sendto(packet, dest)

    def accept_download_request(self, first_packet, s: socket, dest):
        defult_chunk_size, chunk_size = 2048, 2048
        dup_ack_counter, recent_ack_packet_num = 0, 0
        current_read, excepted_sequence_num, request_type = 0, 0, 0
        List = []
        request_type, padded_file_name, excepted_sequence_num, \
            data_length = struct.unpack("h 50s h i", first_packet)
        file_name = str(padded_file_name.decode("ascii")).rstrip("0")
        victim = None
        for i in self.files_list:
            print("file name:" + i)
            if i.__eq__(file_name):
                victim = file_name
        if victim is None:
            self.send_ack(excepted_sequence_num + 1, s, dest, ack_type=200)
            # return
        try:
            file = open(file_name, "rb+")
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0, os.SEEK_SET)
        except:
            raise
        while current_read + chunk_size <= file_size:
            excepted_sequence_num += 1
            List.append((excepted_sequence_num, current_read, current_read + chunk_size))
            current_read += chunk_size
            request_type = 21
            data_length = chunk_size
            packet = struct.pack("2h i " + str(chunk_size) + "s", request_type, excepted_sequence_num,
                                 data_length, file.read(chunk_size))  # .encode("ascii")

            s.sendto(packet, dest)
            ack, address = s.recvfrom(MAX_RECV_BYTES)
            ack_type, excepted_sequence_num = struct.unpack("2h", ack)
            if ack_type != 16:
                print("FRAUD!!!!")
                return
            if excepted_sequence_num == recent_ack_packet_num:
                dup_ack_counter += 1
                if dup_ack_counter == 2:
                    if chunk_size < MAX_SEND_BYTES:
                        chunk_size = int(chunk_size * 1.2)
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
        packet = struct.pack("2h i " + str(chunk_size) + "s", request_type, excepted_sequence_num,
                             data_length, file.read(chunk_size))  # .encode("ascii")
        s.sendto(packet, dest)
        ack, address = s.recvfrom(MAX_RECV_BYTES)
        ack_type, excepted_sequence_num = struct.unpack("2h", ack)
        if ack_type == 17:
            print("finished with: " + str(address[0]))
        file.close()
        return


if __name__ == '__main__':
    rudp_server = RUDPServer()
    rudp_server.server()
