import socket

from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("Your Computer Name is:" + hostname)
print("Your Computer IP Address is:" + IPAddr)


dns_port = 53
SIZE = 2048

while 1:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', dns_port))
    print("waiting for connections...")

    while 1:
        packet, address = s.recvfrom(SIZE)
        domain_name = packet
        # print(domain_name)
        # print(address[0])

        IP_LAYER = IP(dst='8.8.8.8')
        UDP_LAYER = UDP(dport=53)
        DNS_LAYER = DNS(rd=1, qd=DNSQR(qname=domain_name))

        # print("Bytes sent {}".format(t))

        third_layer_packet = IP_LAYER / UDP_LAYER / DNS_LAYER
        send(third_layer_packet)
        ETHERNET_LAYER = Ether()
        second_layer_packet = ETHERNET_LAYER / IP_LAYER / UDP_LAYER / DNS_LAYER
        send(second_layer_packet)
        socket_send = conf.L2socket()
        sendp(second_layer_packet, socket=socket_send)
        packet = srp1(second_layer_packet)
        packet.show()

        s.sendto(IPAddr.encode("ascii"), address)
        break

# packet, address = s.recvfrom(SIZE)
# domain_name = packet.decode()
# print(domain_name)
# print(address[0])
#
#
# IP_LAYER = IP(dst='8.8.8.8')
# UDP_LAYER = UDP(dport = 53)
# # DNS_LAYER = DNS(rd = 1, qd = DNSQR(qname = 'www.moodlearn.ariel.ac.il'))
# DNS_LAYER = DNS(rd = 1, qd = DNSQR(qname = domain_name))
#
# dns_port2 = 68
# dest = (address[0], dns_port2)
# t = s.sendto(IPAddr.encode('ascii'), dest)
# print("Bytes sent {}".format(t))
#
#
# third_layer_packet = IP_LAYER / UDP_LAYER / DNS_LAYER
# send(third_layer_packet)
# ETHERNET_LAYER = Ether()
# second_layer_packet = ETHERNET_LAYER / IP_LAYER / UDP_LAYER / DNS_LAYER
# send(second_layer_packet)
# socket_send = conf.L2socket()
# sendp(second_layer_packet,socket= socket_send)
# packet = srp1(second_layer_packet)
# packet.show()





