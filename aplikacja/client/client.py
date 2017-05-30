# -*- coding: utf-8 -*-

import socket
import sys
import sha3

class Client:
    def __init__(self, nick, my_ip_address, server_ip_address, server_port):
        self.SIZE_OF_BUFFER = 1024
        self.MY_NICK = nick
        self.MY_IP_ADDRESS = my_ip_address
        self.SERVER_IP_ADDRESS = server_ip_address
        self.SERVER_PORT = server_port
        self.CONNECTION = None
        self.CHANNELS_LIST = []
        self.CURRENT_CHANNEL = None
        self.CURRENT_CHANNEL_USERS = []
        self.IAM_ADMIN = False


    # --------------------------    Auxiliary functions      -------------------------------

    def hashAdminPassword(self, password):
        s = sha3.sha3_512()
        s.update(password)
        return s.hexdigest().decode('utf-8')

    def receiveSafe(self):
        """
        For safe receiving data. Set timeouts
        """
        self.CONNECTION.settimeout(10.0)
        try:
            response = self.CONNECTION.recv(self.SIZE_OF_BUFFER).decode('utf-8')
            print("\tKomunikat:" + response)
        except:
            # time exceeded
            return False
        self.CONNECTION.settimeout(None)
        return response.split(" ")
    


    # --------------------------------------------------------------------------------------


    def connect(self, admin_password):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.SERVER_IP_ADDRESS, self.SERVER_PORT))
        except Exception as e:
            print("\n-- Could not connect to server", str(e))
            return False

        admin_password = self.hashAdminPassword(admin_password)
        s.settimeout(10.0)
        s.send(b"CONNECT " + self.MY_NICK.encode('utf-8') + b" " + admin_password.encode('utf-8'))
        try:
            response = s.recv(self.SIZE_OF_BUFFER).decode('utf-8')
        except:
            print("-- Connection error")
            return False
        s.settimeout(None)

        if response == "CONNECTED":
            self.CONNECTION = s
            return True
        elif response == "CONNECTED-a":
            self.CONNECTION = s
            self.IAM_ADMIN = True
            return True

        elif response == "NOT_CONNECTED":
            print("NOT_CONNECTED nick is busy or blocked")
            return False
        else:
            print(response)
            return False

    def getChannelsList(self):
        self.CONNECTION.send(b"ASK_CHANNELS")
        response = self.receiveSafe()

        if response[0] == "CHANNELS":
            channels = response[1].split(",")

            self.CHANNELS_LIST = []
            for i in channels:
                self.CHANNELS_LIST.append(i)
        else:
            print(';'.join(response))

    def joinChannel(self, channel_name, password):
        self.CONNECTION.send(b"JOIN " + channel_name.encode('utf-8') + b" " + password.encode('utf-8'))
        response = self.receiveSafe()


        if response[0] == "JOINED":
            self.CURRENT_CHANNEL = channel_name
            # tutaj bedzie polaczenie audio
            return True
        elif response[0] == "NOT_JOINED":
            print("-- Invalid password")
            return False
        else:
            print(' '.join(response))
            return False


    def getChannelUsers(self, channel_name):
        self.CONNECTION.send(b"ASK_CHAN_USERS " + channel_name.encode('utf-8'))
        response = self.receiveSafe()


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

        if response[0] == "CHAN_EXITED":
            print("-- You left channel")
            self.CURRENT_CHANNEL_USERS = []
            self.CURRENT_CHANNEL = None
            return True
        else:
            print(' '.join(response))
            return False

    def disconnect(self):
        self.CONNECTION.send(b"DISCONNECT")
        response = self.receiveSafe()

        if response[0] == "DISCONNECTED":
            print("-- You left server")
            self.CURRENT_CHANNEL_USERS = []
            self.CURRENT_CHANNEL = None
            self.CHANNELS_LIST = []
            self.CONNECTION.close()
            return True
        else:
            print(' '.join(response))
            return False


    # -----------------   ADMIN    ------------------------------------

    def addChannel(self, channel_name, channel_password):
        self.CONNECTION.send(b"ADD_CHANNEL " + b" " + channel_name.encode('utf-8')
            + b" " + channel_password.encode('utf-8'))

        response = self.receiveSafe()
        if response[0] == "ACK_ADMIN":
            print("-- Channel added to list")
        else:
            print(' '.join(response))

    def delChannel(self, channel_name):
        self.CONNECTION.send(b"DEL_CHANNEL " + b" " + channel_name.encode('utf-8'))
        response = self.receiveSafe()
        if response[0] == "ACK_ADMIN":
            print("-- Channel deleted")
        else:
            print(' '.join(response))

    def blockIP(self, ip_address):
        self.CONNECTION.send(b"BLOCK_IP " + b" " + ip_address.encode('utf-8'))
        response = self.receiveSafe()
        if response[0] == "ACK_ADMIN":
            print("-- IP blocked")
            return True
        else:
            print(' '.join(response))
            return False

    def unblockIP(self, ip_address):
        self.CONNECTION.send(b"UNBLOCK_IP " + b" " + ip_address.encode('utf-8'))
        response = self.receiveSafe()
        if response[0] == "ACK_ADMIN":
            print("-- IP unblocked")
            return True
        else:
            print(' '.join(response))
            return False

    def blockNick(self, nick):
        self.CONNECTION.send(b"BLOCK_NICK " + b" " + nick.encode('utf-8'))
        response = self.receiveSafe()
        if response[0] == "ACK_ADMIN":
            print("-- Nick blocked")
            return True
        else:
            print(' '.join(response))
            return False

    def unblockNick(self, nick):
        self.CONNECTION.send(b"UNBLOCK_NICK " + b" " + nick.encode('utf-8'))
        response = self.receiveSafe()
        if response[0] == "ACK_ADMIN":
            print("-- Nick unblocked")
            return True
        else:
            print(' '.join(response))
            return False



    # --------------------    TEST methods   -------------------------
    def print_vars(self):
        for k, v in vars(self).items():
            print(str(k) + ":\t" + str(v))

    def help(self):
        print("""
                    USER
                c - connect to server
                gcl - get channels list
                jc - join channel
                gcu - get channel users
                ec - exit channel
                d - disconnect

                    ADMIN
                addc - add channel
                delc - delete channel
                bip - block ip
                ubip - unblock ip
                bn - block nickname
                ubn - unblock nickname

                h - help
                q - exit program
                v - print all class variables
            """)
        
    def test(self):
        self.help()
        while True:
            try:
                opt = input("Option: ")
                opt = opt.split(" ")
                if opt[0] == "c":
                    self.connect()
                elif opt[0] == "gcl":
                    self.getChannelsList()
                elif opt[0] == "jc":
                    chan = input("Channel name: ")
                    chan_pass = input("Channel password: ")
                    self.joinChannel(chan, chan_pass)
                elif opt[0] == "gcu":
                    chan = input("Channel name: ")
                    self.getChannelUsers(chan)
                elif opt[0] == "ec":
                    self.exitChannel()
                elif opt[0] == "d":
                    self.disconnect()
                elif opt[0] == "v":
                    self.print_vars()
                elif opt[0] == "q":
                    return
                elif opt[0] == "h":
                    self.help()
                elif opt[0] == "addc":
                    admin_pass = input("Admin password: ")
                    admin_pass = self.hashAdminPassword(admin_pass)
                    chan = input("Channel name: ")
                    chan_pass = input("Channel password: ")
                    self.addChannel(admin_pass, chan, chan_pass)
                elif opt[0] == "delc":
                    admin_pass = input("Admin password: ")
                    admin_pass = self.hashAdminPassword(admin_pass)
                    chan = input("Channel name: ")
                    self.delChannel(admin_pass, chan)
                elif opt[0] == "bip":
                    admin_pass = input("Admin password: ")
                    admin_pass = self.hashAdminPassword(admin_pass)
                    ip = input("IP address: ")
                    self.blockIP(admin_pass, ip)
                elif opt[0] == "ubip":
                    admin_pass = input("Admin password: ")
                    admin_pass = self.hashAdminPassword(admin_pass)
                    ip = input("IP address: ")
                    self.unblockIP(admin_pass, ip)
                elif opt[0] == "bn":
                    admin_pass = input("Admin password: ")
                    admin_pass = self.hashAdminPassword(admin_pass)
                    nick = input("Nickname: ")
                    self.blockNick(admin_pass, nick)
                elif opt[0] == "ubn":
                    admin_pass = input("Admin password: ")
                    admin_pass = self.hashAdminPassword(admin_pass)
                    nick = input("Nickname: ")
                    self.unblockNick(admin_pass, nick)
                else:
                    print("Choose option")
            except Exception as e:
                print("\nBad parameter " + str(e))



if __name__ == "__main__": 
    k = Client("krzysiek", "127.0.0.1", "127.0.0.1", 50000) 
    k.test()