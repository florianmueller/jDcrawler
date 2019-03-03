import unittest
from utilities import get_ftp_connection, host, port, username, passwd
import ftplib

class FTPTest(unittest.TestCase):
    ftp = None

    def setUp(self):
        FTPTest.ftp = get_ftp_connection(host=host, port=port, username=username, password=passwd)
        print(FTPTest.ftp.getwelcome())

    def testFTPconnection(self):
        self.assertIsNotNone(FTPTest.ftp)
        self.assertIsInstance(FTPTest.ftp, ftplib.FTP)

    # def testLoginSuccessful(self):
    #     self.

