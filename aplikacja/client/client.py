# -*- coding: utf-8 -*-

import socket
import sys
import sha3
import threading
from audio import Audio
import time
from queue import Queue

class Client:
    def __init__(self, nick, server_ip_address, server_port, udp_port):
        self.SIZE_OF_BUFFER = 1024
        self.MY_NICK = nick
        self.MY_IP_ADDRESS = None
        self.SERVER_IP_ADDRESS = server_ip_address
        self.SERVER_PORT = server_port
        self.CONNECTION = None
        self.CHANNELS_LIST = []
        self.CURRENT_CHANNEL = None
        self.CURRENT_CHANNEL_USERS = []
        self.IAM_ADMIN = False

        # audio UDP
        self.UDP_CONNECTION = None
        self.UDP_PORT = udp_port
        self.AUDIO_LOCK = False
        self.AUDIO = None



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

        self.MY_IP_ADDRESS = str(s.getsockname()[0])
        admin_password = self.hashAdminPassword(admin_password)
        s.settimeout(10.0)
        s.send(b"CONNECT " + self.MY_NICK.encode('utf-8') + b" " + admin_password.encode('utf-8'))
        self.udp_connection()
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

    def udp_connection(self):
        self.UDP_CONNECTION = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDP_CONNECTION.sendto(b"siemka", (self.SERVER_IP_ADDRESS, self.UDP_PORT))

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
        self.AUDIO_LOCK = False  # stop previous audio stream
        self.CONNECTION.send(b"JOIN " + channel_name.encode('utf-8') + b" " + password.encode('utf-8'))
        response = self.receiveSafe()


        if response[0] == "JOINED":
            self.CURRENT_CHANNEL = channel_name
            # !!!
            
            #self.AUDIO = Audio()
            self.AUDIO_LOCK = True
            t_record = threading.Thread(target=self.record_and_send, args = ())
            t_player = threading.Thread(target=self.receive_and_play, args = ())
            t_record.start()
            t_player.start()
            
            # !!!
            return True
        elif response[0] == "NOT_JOINED":
            print("-- Invalid password")
            return False
        else:
            print(' '.join(response))
            return False

    # ------------------------   UDP AUDIO   --------------------------------------
    def record_and_send(self): # record and send voice
        print("Wysylanie audio")
        while self.AUDIO_LOCK:
            try:
                #data = self.AUDIO.record()
                data = b"Stacjonarka"
                self.UDP_CONNECTION.sendto(data, (self.SERVER_IP_ADDRESS, self.UDP_PORT))
                print("Wysłane:", data)
                time.sleep(2)
            except Exception as e:
                print("UDP sending error:", e)
        if self.AUDIO is not None:  # close audio stream
            self.AUDIO.exit()

    def receive_and_play(self):
        print("Odbieranie audio")
        while self.AUDIO_LOCK:
            try:
                self.UDP_CONNECTION.settimeout(5)
                data, _ = self.UDP_CONNECTION.recvfrom(self.SIZE_OF_BUFFER)
                self.UDP_CONNECTION.settimeout(None)
                #self.AUDIO.play(data)
                print(data.decode('utf-8'))
                time.sleep(2)
            except socket.timeout:
                print("NIC NIE DOSTAŁEM :(")
                continue
            except:
                pass
        if self.AUDIO is not None:  # close audio stream
            self.AUDIO.exit()

    # -----------------------------------------------------------------------------


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
        self.AUDIO_LOCK = False  # stop audio stream
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
        self.AUDIO_LOCK = False  # stop audio stream
        self.CONNECTION.send(b"DISCONNECT")
        response = self.receiveSafe()

        if response[0] == "DISCONNECTED":
            print("-- You left server")
            self.CURRENT_CHANNEL_USERS = []
            self.CURRENT_CHANNEL = None
            self.CHANNELS_LIST = []
            self.CONNECTION.close()
            if self.UDP_CONNECTION is not None:
                self.UDP_CONNECTION.close()
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



if __name__ == "__main__": 
    k = Client("krzysiek", "127.0.0.1", "127.0.0.1", 50000) 
    k.test()