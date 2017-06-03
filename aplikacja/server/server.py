# -*- coding: utf-8 -*-
import sys
import socket
import threading
import models
import sha3
from queue import Queue, Empty
import traceback


class Server:
    def __init__(self):
        # technical parameters
        self.SIZE_OF_BUFFER = 1024  # max size of packets sending through socket
        self.SERVER_IP = '192.168.0.12'
        self.SERVER_PORT = 50000
        self.SERVER_PORT_UDP = 60000
        self.MAX_USERS = 5
        self.SERVER = None  # TCP socket
        self.GLOBAL_THREAD_LOCK = True

        # logical parameters
        self.DATABASE = models.database_connect()
        self.ADMIN_PASSWORD = None


        """
        self.BIG_LIST = {
                        "kanal1": [Queue(), udp_socket, port], "kanal2": [Queue(), udp_socket, port]
                        }
        """
        self.BIG_LIST = {}
        """
        self.USERS_IN_CHANNEL = {
                    "kanal1": [
                                ["192.168.0.12", 67890],
                                ["192.168.0.11", 12345]
                            ]
                    }
        """
        self.USERS_IN_CHANNEL = {}
        self.UDP_PORT_NUMBERS = 60001


    # --------------------------    Auxiliary functions      -------------------------------

    def setAdminPassword(self, password):
        s = sha3.sha3_512()
        s.update(password)
        self.ADMIN_PASSWORD = s.hexdigest().decode('utf-8')

    def checkAdminPassword(self, password):
        if self.ADMIN_PASSWORD == password:
            return True
        else:
            return False

    # ------------- BIG LIST ---- AND ---- USERS IN CHANNEL ----------------

    def set_BIG_LIST(self):
        chans = self.DATABASE.query(models.Channel).all()
        for chan in chans:
            if chan.name not in self.BIG_LIST:
                sock = self.open_UDP_socket(self.UDP_PORT_NUMBERS)
                self.BIG_LIST[chan.name] = [Queue(), sock, self.UDP_PORT_NUMBERS]
                self.UDP_PORT_NUMBERS += 1

                t_receive = threading.Thread(target=self.receiving_robot, args=(chan.name,))
                t_send = threading.Thread(target=self.sending_robot, args=(chan.name,))
                t_receive.start()
                t_send.start()
            if chan.name not in self.USERS_IN_CHANNEL:
                self.USERS_IN_CHANNEL[chan.name] = []  # set empty list for all channels

    # ------------------------------------------------------------------------------------

    def open_TCP_socket(self):
        """
        Initialization socket
        """
        try:
            self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.SERVER.bind((self.SERVER_IP, self.SERVER_PORT))
            self.SERVER.listen(self.MAX_USERS)
        except Exception as e:
            print("\n-- Could not open TCP socket", str(e))
            sys.exit(1)
        print("\n-- TCP socket opened on " + str(self.SERVER_IP) + ":" + str(self.SERVER_PORT))


    # ----------------------   UDP connection   --------------------------

    def open_UDP_socket(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.SERVER_IP, port))
        except Exception as e:
            print("\n-- Could not open UDP socket on", port, "with error:", str(e))
            sys.exit(1)
        print("\n-- UDP socket opened on " + str(self.SERVER_IP) + ":" + str(port))
        return sock


    def receiving_robot(self, channel):
        sock = self.BIG_LIST[channel][1]
        sock.settimeout(1)
        while self.GLOBAL_THREAD_LOCK:
            try:
                data, addr = sock.recvfrom(1024)
                print("Odebrano:", data.decode('utf-8'))
            except socket.timeout:
                continue
            packet = [addr[0], data]
            self.BIG_LIST[channel][0].put(packet)

    def sending_robot(self, channel):
        sock = self.BIG_LIST[channel][1]
        while self.GLOBAL_THREAD_LOCK:
            try:
                ip, data = self.BIG_LIST[channel][0].get(timeout=1)
            except Empty:
                continue
            for usr in self.USERS_IN_CHANNEL[channel]:
                if usr[0] != ip:
                    sock.sendto(data, (usr[0],usr[1]))
                    print("UDP wyslano:", usr)

    #  ----------------------------------------------------------------------

    def commands(self, comm, params_list, user_obj):
        """
        Depending on the 'comm' operate on 'params_list'
        
        comm - command for example "CONNECT"
        params_list - for example ['channel_name', 'password']
        user_obj - User object
        """
        if comm == "ASK_CHANNELS":
            """
            Ask abount channels list
            example: ASK_CHANNELS
            """
            tmp_list = [i.name for i in self.DATABASE.query(models.Channel).all()]
            chan_list = ','.join(tmp_list)
            return "CHANNELS " + chan_list

        elif comm == "JOIN":
            """
            Request for join channel
            example: JOIN name password udp_port
            """
            if len(params_list)<3:
                return "ERROR channel name or password not given"

            channel = self.DATABASE.query(models.Channel).filter_by(name=params_list[0]).first()
            old_channel = self.DATABASE.query(models.Channel).filter_by(id=user_obj.channel_id).first()
            if channel is None:
                return "ERROR channel does not exists"
            if params_list[1] == channel.password:  # CHECK PASSWORD: TODO encryption ???
                if user_obj.channel_id == channel.id:
                    return "ERROR you are in this channel" # user was and is in channel
                else:
                    tmp = [user_obj.ip_address, int(params_list[2])]
                    if old_channel is not None and tmp in self.USERS_IN_CHANNEL[old_channel.name]:
                        self.USERS_IN_CHANNEL[old_channel.name].remove(tmp)
                    user_obj.channel_id = channel.id  # changing channel
                    self.USERS_IN_CHANNEL[channel.name].append(tmp)
                    self.DATABASE.commit()
                    return "JOINED " + str(self.BIG_LIST[channel.name][2])
            else:
                return "NOT_JOINED"

        elif comm == "ASK_CHAN_USERS":
            """
            Ask abount users on the channel
            ASK_CHAN_USERS channel_name
            """
            if len(params_list)<1:
                return "ERROR channel name not give"
            channel = self.DATABASE.query(models.Channel).filter_by(name=params_list[0]).first()
            if channel is None:
                return "ERROR channel does not exists"

            users_list = ','.join([i.nick for i in channel.users])
            return "CHAN_USERS " + users_list

        elif comm == "CHAN_EXIT":
            """
            Request for delete user from channel
            """
            user_obj.channel = None
            self.DATABASE.commit()
            return "CHAN_EXITED"

        elif comm == "DISCONNECT":
            """
            Request for delete user from server users list
            example: DISCONNECT
            """
            user_obj.channel = None
            self.DATABASE.delete(user_obj)
            self.DATABASE.commit()
            self.DATABASE.close()  # close database connection for this thread
            return "DISCONNECTED"

        # -----------------------------    ADMIN    -----------------------

        elif comm == "ADD_CHANNEL":
            """
            Request for add channel
            """
            if len(params_list)<2:
                return "ERROR not enough parameters"
            
            if self.DATABASE.query(models.Channel).filter_by(name=params_list[1]).first() is not None:
                return "ERROR channel exists"

            chan = models.Channel(params_list[1], params_list[2], "")
            self.DATABASE.add(chan)
            self.DATABASE.commit()
            self.set_BIG_LIST()
            return "ACK_ADMIN"

        elif comm == "DEL_CHANNEL":
            """
            Request for delete channel
            """
            if len(params_list)<1:
                return "ERROR not enough parameters"

            chan = self.DATABASE.query(models.Channel).filter_by(name=params_list[1]).first()
            if chan is not None:
                self.DATABASE.delete(chan)
                self.DATABASE.commit()
                return "ACK_ADMIN"

        elif comm == "BLOCK_IP":
            """
            Request for block IP address
            """
            if len(params_list)<1:
                print(len(params_list))
                return "ERROR not enough parameters"

            ban = models.Black_IP(params_list[1], "")
            self.DATABASE.add(ban)
            self.DATABASE.commit()
            return "ACK_ADMIN"

        elif comm == "UNBLOCK_IP":
            """
            Request for unblock IP address
            """
            if len(params_list)<1:
                print(len(params_list))
                return "ERROR not enough parameters"

            unban = self.DATABASE.query(models.Black_IP).filter_by(ip=params_list[1]).first()
            if unban is not None:
                self.DATABASE.delete(unban)
                self.DATABASE.commit()
            return "ACK_ADMIN"

        elif comm == "BLOCK_NICK":
            """
            Request for block nickname
            """
            if len(params_list)<1:
                return "ERROR not enough parameters"

            ban = models.Black_Nick(params_list[1], "")
            self.DATABASE.add(ban)
            self.DATABASE.commit()
            return "ACK_ADMIN"

        elif comm == "UNBLOCK_NICK":
            """
            Request for unblock nickname
            """
            if len(params_list)<1:
                return "ERROR not enough parameters"

            unban = self.DATABASE.query(models.Black_Nick).filter_by(nick=params_list[1]).first()
            if unban is not None:
                self.DATABASE.delete(unban)
                self.DATABASE.commit()
            return "ACK_ADMIN"

        else:
            print("-- Unknow command:", comm)
            return "Unknow command: " + comm

    def login(self, client, ip):
        """
        Save user in database and take his ID
        """
        user_id = None  # User ID from the database
        client.settimeout(10.0)
        try:
            data = client.recv(self.SIZE_OF_BUFFER)  # expected command: CONNECT name
        except Exception as e:
            print("-- Timeout exceeded:", e)
            return "Timeout exceeded", None
        client.settimeout(None)
        comm = data.decode('utf-8').split(" ")[0]
        params_list = data.decode('utf-8').split(" ")[1:]

        if comm == "CONNECT":
            """
            Connect to server with nick
            example: CONNECT name
            """
            if len(params_list)<1:
                return "ERROR no nick given", None

            nick = params_list[0]
            is_admin = False
            if len(params_list) == 2 and self.checkAdminPassword(params_list[1]):
                is_admin = True


            if self.DATABASE.query(models.User).filter_by(nick=nick).first() is not None or\
                self.DATABASE.query(models.Black_Nick).filter_by(nick=nick).first() is not None:
                """
                nick is busy or blocked
                """
                return "NOT_CONNECTED", None

            try:
                self.DATABASE.add(models.User(nick, ip, is_admin))
                self.DATABASE.commit()
                user_id = self.DATABASE.query(models.User).filter_by(nick=nick).first()
                if user_id.is_admin:
                    print("--Admin login")
                    return "CONNECTED-a", user_id.id
                else:
                    print("--Normal user login")
                    return "CONNECTED", user_id.id
            except:
                self.DATABASE.rollback()
                return "ERROR database integrity error", None
        else:
            print("-- Please login first")
            return "ERROR login first", None


    def management_connection(self,client):
        """
        Manage and control connection with client.
        Processes commands from client.
        """
        ip, port = client.getpeername()  # ip and port of client
        message, client_id = self.login(client, ip)
        if client_id is not None:
            client.send(message.encode('utf-8'))  # login successful
            user_obj = self.DATABASE.query(models.User).filter_by(id=client_id).first()  # get User object
        else:
            client.send(message.encode('utf-8'))  # login NOT successful
            client.close()
            self.DATABASE.close()  # close database connection for this thread
            return

        while True:
            try:
                data = client.recv(self.SIZE_OF_BUFFER)
                if data:
                    comm = data.decode('utf-8').split(" ")[0]
                    params_list = data.decode('utf-8').split(" ")[1:]

                    response = self.commands(comm, params_list, user_obj)
                    client.send(response.encode('utf-8'))  # send response to client

                    if response == "DISCONNECTED":
                        client.close()
                        print("# Klient " + ip + " rozłączył się")
                        return
                else:
                    client.close()
                    self.DATABASE.delete(user_obj)
                    self.DATABASE.commit()
                    self.DATABASE.close()  # close database connection for this thread
                    print("# Klient " + ip + " zerwał połączenie")
                    return
            except Exception as e:
                client.close()
                self.DATABASE.delete(user_obj)
                self.DATABASE.commit()
                self.DATABASE.close()  # close database connection for this thread
                print("\n-- Management_connection error: ", str(e))
                traceback.print_exc()
                return


    def run(self):
        """
        Listen to new connection and run threads for them.
        """
        self.setAdminPassword("admin")
        self.open_TCP_socket()
        self.set_BIG_LIST()
        while True:
            try:
                client, address = self.SERVER.accept()
                if self.DATABASE.query(models.Black_IP).filter_by(ip=address[0]).first() is not None:
                    client.close()
                    continue
                print("-- New connection: " + address[0])
                t=threading.Thread(target=self.management_connection, args = (client,))
                t.start()
            except KeyboardInterrupt:
                self.GLOBAL_THREAD_LOCK = False
                self.DATABASE.close()
                self.SERVER.close()
                print("\n-- Closing server")
                sys.exit(0)
            except:
                self.GLOBAL_THREAD_LOCK = False
                self.DATABASE.close()
                self.SERVER.close()
                print("\n-- Force closing server")
                sys.exit(0)


if __name__ == "__main__": 
    s = Server() 
    s.run()