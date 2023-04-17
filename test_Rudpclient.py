import struct
import unittest
from time import sleep
from unittest import TestCase

from Rudpclient import RUDPClient
import filecmp
from test import *

rudp = RUDPClient()


class testsclient(unittest.TestCase):

    def test_pack_discover(self):
        PTYPE = 0
        packet_expected = struct.pack("i i", PTYPE, 20)
        packet_get = rudp.pack_discover()

        self.assertEqual(packet_get, packet_expected)

    def test_pack_request(self):
        PTYPE = 4
        packet_expected = struct.pack("h i", PTYPE, "127.0.0.1")
        packet_get = rudp.pack_request("127.0.0.1")

        self.assertEqual(packet_get, packet_expected)



    def test_unpack_ack(self):
        assert False

    def test_download_request(self):
        filename1 = "onmb2.txt"
        filename2 = "OneMb2.txt"

        rudp.download_request(filename2, filename1)
        sleep(2)

        self.assertTrue(filecmp.cmp(filename2, filename1), 'Error in download_request file')

    def test_send_ack(self):
        assert False

    def test_upload_request(self):
        filename1 = "bcdes1.txt"
        filename2 = "bcdes.txt"

        rudp.upload_request(filename2, filename1)
        sleep(2)
        self.assertTrue(filecmp.cmp(filename2, filename1), 'Error in upload_request file')


if __name__ == '__main__':
    unittest.main()
