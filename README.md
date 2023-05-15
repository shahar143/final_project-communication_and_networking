# Final Project for Communication and Networking course
University final assignment for Networking and Communication course.

### For Computer Science B.S.c Ariel University

## Team members

- Shahar Zaidel 211990700 
- Mohanad Safi 208113381

## Description
In this project we implemented  FTP application based on RUDP communication.
The code contains a server side app and a client side app.
This project test the ability to implement a reliable data transfer protocol on top of UDP only.

our protocol is supporting the following features:
1. It uses Congestion Control algorithms to control the flow of data.
2. It calculates the RTT for each packet and uses it to understand the network conditions and act accordingly.
3. The server knows to increase and decrease the packet size it sends according to the network conditions.

For more information about the protocol please read our detailed pdf report named:
"ftp app- detailed pdf.pdf"

### DHCP server

In this project we implemented a DHCP server.
The dhcp server return full configuration to the client, 
including: ip address, subnet mask, default gateway and lease time.

The rudp client won't be able to send data to the server until it will get a valid ip address from the dhcp server.

## DNS server

In this project we implemented a DNS server.
The DNS server uses SCAPY library to send DNS queries to the DNS server.
The DNS server will return the ip address of the requested domain name.

### RUDP server

The RUDP server is the server side of our FTP application.

Our FTP application supports: 
1. Upload file from the client to the server.
2. Download file from the server to the client.
3. List all files in the server.
4. Delete file from the server.

### RUDP client

The RUDP client is the client side of our FTP application.

The client side connection steps: 
1. The client will get full configuration from the DHCP server.
2. The client will send a DNS query to the DNS server to get the ip address of the server.
3. The client will start the connection with the server.

## How to run

Run the following commands in a different terminal:
- Note: 
- run the files in the following order. it is very important.
- you need to use sudo while running the commands.
- You'll need 4 terminal windows in total.


1. Run the DHCP server:
    ```bash
    sudo python3 dhcpserver.py
    ```
2. Run the DNS server:
    ```bash
    sudo python3 dnsserver.py
    ```
3. Run the RUDP server:
    ```bash
    sudo python3 Rudpserver.py
    ```
4. Run the RUDP client:
    ```bash
    sudo python3 guard_thread.py
    ```

In order to sign-in to the FTP application can register a new user or use the following credentials:
- username: shahar
- password: aaaaaa

### Requirements
- Full linux environment - not WSL or any other windows based linux environment.
- Python 3.10
- Scapy - version 2.4.4

In order to install Scapy run the following command:
```bash
    sudo apt install python3-scapy
```
Or: 

```bash
    pip3 install scapy
```

### Packet loss tool
If you wish, you can test our RUDP application with a packet loss tool.
We used iproute2: 

In order to install iproute2 run the following command:

We recommend to use the following command before installing iproute2:
```bash
    sudo apt-get update
```
```bash
    sudo apt install iproute2
```

- a command for setting a packet-loss rate:
```bash
    sudo tc qdisc add dev lo root netem loss XX%
```
- a command for changing the packet-loss rate:
```bash
    sudo tc qdisc change dev lo root netem loss XX%
```
- a command for disabling the packet-loss rate:
```bash
    sudo tc qdisc del dev lo root netem
```
