import socket
import struct
import threading
import time

serverPort = 67
clientPort = 68
available_addresses = [(0, 0)] * 255
MAX_RECV_BYTES = 65535


def occupied_ip_addresses():
    for i in range(1, 255):
        if available_addresses[i][0] == 0:
            available_addresses[i] = (1, 0)
            return i
    return -1


def release_IP_addresses():
    counter = 0
    for i in range(1, 255):
        if available_addresses[i][1] + 43200 >= time.time() and available_addresses[i][1] != 0:
            available_addresses[i] = (0, 0)
            counter += 1
    print("released " + str(counter) + " addresses")


def dhcp_thread():
    while 1:
        release_IP_addresses()
        time.sleep(7200)


class DHCP_server(object):

    def server(self):
        print("DHCP server is starting...\n")

        thread = threading.Thread(target=dhcp_thread)
        thread.start()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(('', serverPort))
        dest = ('255.255.255.255', clientPort)

        while 1:
            try:
                print("waiting for DHCP discovery...")
                data, address = s.recvfrom(MAX_RECV_BYTES)
                TID = self.unpack_discovery(data)
                if TID == -1:
                    print("FRAUD!!!")
                    return
                print("received DHCP discovery")

                print("Sending DHCP offer")
                data = self.pack_offer(TID)
                s.sendto(data, dest)
                while 1:
                    try:
                        print("waiting for DHCP request...")
                        data, address = s.recvfrom(MAX_RECV_BYTES)
                        string = self.unpack_request(data, TID)
                        print("received DHCP request")

                        print("Sending DHCP ack\n")
                        # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                        dest = (address[0], clientPort)
                        data = self.pack_ack(string, TID)
                        s.sendto(data, dest)
                        break
                    except:
                        raise
            except:
                raise

    def unpack_discovery(self, packet):
        PTYPE, tid = "", ""
        try:
            PTYPE, tid = struct.unpack("s 8s", packet)
        except:
            pass
        TID = tid.decode("ascii")
        if PTYPE.decode("ascii") != "0":
            print("wrong address")
            exit(-1)
        return TID

    def pack_offer(self, TID):
        PTYPE = "3"
        OIPADDR = occupied_ip_addresses()
        ODFLTGTWY = "192.168.1.1".encode("ascii")
        OSBNTMSK = "255.255.255.0".encode("ascii")
        LEASETIME = 43200

        package = struct.pack("s 8s i 11s 13s i", PTYPE.encode("ascii"), TID.encode("ascii"), OIPADDR,
                              ODFLTGTWY, OSBNTMSK, LEASETIME)
        return package

    def unpack_request(self, packet, TID):
        IPADDR = 0
        try:
            PTYPE, tid, IPADDR = struct.unpack("s 8s i", packet)
            if tid.decode("ascii") != TID:
                print("FRAUD!!!")
                exit(-1)
            if PTYPE.decode("ascii") != "4":
                print("wrong address")
                exit(-1)
        except:
            pass
        if not available_addresses[IPADDR][0] == 1 or IPADDR == -1:
            print("sorry, currently unavailable")
            return "9"
        available_addresses[int(IPADDR)] = (1, time.time())
        return "7"

    def pack_ack(self, string, TID):
        PTYPE = ''
        if string == "9":
            PTYPE = "9"
        elif string == "7":
            PTYPE = "7"
        packet = struct.pack("s 8s", PTYPE.encode("ascii"), TID.encode("ascii"))
        return packet


if __name__ == '__main__':
    dhcp_server = DHCP_server()
    dhcp_server.server()
