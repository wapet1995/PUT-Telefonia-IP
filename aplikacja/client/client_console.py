# -*- coding: utf-8 -*-

import socket
import sys


class Client:
    def __init__(self, my_name, my_ip_address, server_ip_address, server_port):
        self.SIZE_OF_BUFFER = 1024
        self.MY_NAME = my_name
        self.MY_IP_ADDRESS = my_ip_address
        self.SERVER_IP_ADDRESS = server_ip_address
        self.SERVER_PORT = server_port
        self.CONNECTION = None
        self.CHANNELS_LIST = []
        self.CURRENT_CHANNEL = None
        self.CURRENT_CHANNEL_USERS = []


    # --------------------------    Auxiliary functions      -------------------------------

    def receiveSafe(self):
        """
        For safe receiving data. Set timeouts
        """
        self.CONNECTION.settimeout(10.0)
        try:
            response = self.CONNECTION.recv(self.SIZE_OF_BUFFER).decode('utf-8')
        except:
            # time exceeded
            return False
        self.CONNECTION.settimeout(None)
        return response
    


    # --------------------------------------------------------------------------------------


    def connect(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.SERVER_IP_ADDRESS, self.SERVER_PORT))
        except Exception as e:
            print("\n-- Could not connect to server", str(e))
            return False

        s.settimeout(10.0)
        # send nick
        s.send(b"CONNECT " + self.MY_NAME.encode('utf-8'))
        try:
            response = s.recv(self.SIZE_OF_BUFFER)
        except:
            print("-- Connection error")
            return False
        s.settimeout(None)

        if response.decode('utf-8') == "CONNECTED":
            self.MY_NAME = self.MY_NAME
            self.CONNECTION = s
            return True
        elif response.decode('utf-8') == "NOT_CONNECTED":
            print("NOT_CONNECTED nick is busy or blocked")
            return False
        else:
            print(response.decode('utf-8'))
            return False

    def getChannelsList(self):
        self.CONNECTION.send(b"ASK_CHANNELS")
        response = self.receiveSafe()

        response = response.split(" ")
        if response[0] == "CHANNELS":
            channels = response[1].split(",")

            self.CHANNELS_LIST = []
            for i in channels:
                self.CHANNELS_LIST.append(i)
        else:
            print(' '.join(response))

    def joinChannel(self, channel_name, password):
        self.CONNECTION.send(b"JOIN " + channel_name.encode('utf-8') + b" " + password.encode('utf-8'))
        response = self.receiveSafe()

        response = response.split(" ")
        if response[0] == "JOINED":
            self.CURRENT_CHANNEL = channel_name
            # tutaj bedzie polaczenie audio
        elif response[0] == "NOT_JOINED":
            print("-- Invalid password")
        else:
            print(' '.join(response))


    def getChannelUsers(self, channel_name):
        self.CONNECTION.send(b"ASK_CHAN_USERS " + channel_name.encode('utf-8'))
        response = self.receiveSafe()
        response = response.split(" ")

        if response[0] == "CHAN_USERS":
            users = response[1].split(",")

            self.CURRENT_CHANNEL_USERS = []
            for i in users:
                self.CURRENT_CHANNEL_USERS.append(i)
        else:
            print(' '.join(response))

    def exitChannel(self):
        self.CONNECTION.send(b"CHAN_EXIT")
        response = self.receiveSafe()
        response = response.split(" ")
        if response[0] == "CHAN_EXITED":
            print("-- You left channel")
            self.CURRENT_CHANNEL_USERS = []
            self.CURRENT_CHANNEL = None
        else:
            print(' '.join(response))

    def disconnect(self):
        self.CONNECTION.send(b"DISCONNECT")
        response = self.receiveSafe()
        response = response.split(" ")
        if response[0] == "DISCONNECTED":
            print("-- You left server")
            self.CURRENT_CHANNEL_USERS = []
            self.CURRENT_CHANNEL = None
            self.CHANNELS_LIST = []
            self.CONNECTION.close()
        else:
            print(' '.join(response))


    # --------------------    TEST methods   -------------------------
    def print_vars(self):
        for k, v in vars(self).items():
            print(str(k) + ":\t" + str(v))
        
    def test(self):
        print("""
                c - connect to server
                gcl - get channels list
                jc [channel_name] [password] - join channel
                gcu [channel_name] - ask about users in channel
                ec - exit from channel
                d - disconnect from server
                q - exit program,
                v - print all class variables
            """)
        while True:
            try:
                opt = input("Opcja: ")
                opt = opt.split(" ")
                if opt[0] == "c":
                    self.connect()
                elif opt[0] == "gcl":
                    self.getChannelsList()
                elif opt[0] == "jc":
                    self.joinChannel(opt[1], opt[2])
                elif opt[0] == "gcu":
                    self.getChannelUsers(opt[1])
                elif opt[0] == "ec":
                    self.exitChannel()
                elif opt[0] == "d":
                    self.disconnect()
                elif opt[0] == "v":
                    self.print_vars()
                elif opt[0] == "q":
                    return
                else:
                    print("""
                        c - connect to server
                        gcl - get channels list
                        jc [channel_name] [password] - join channel
                        gcu [channel_name] - ask about users in channel
                        ec - exit from channel
                        d - disconnect from server
                        q - exit program,
                        v - print all class variables
                    """)
            except:
                print("\nBad parameter")



if __name__ == "__main__": 
    k = Client("krzysiek", "127.0.0.1", "127.0.0.1", 50000) 
    k.test()