# -*- coding: utf-8 -*-
import sys
import socket
import threading
import models


class Server:
    def __init__(self):
        # technical parameters
        self.SIZE_OF_BUFFER = 1024  # max size of packets sending through socket
        self.SERVER_IP = '127.0.0.1'
        self.SERVER_PORT = 50000
        self.MAX_USERS = 5
        self.SERVER = None
        self.THREADS_LOCK = True

        # logical parameters
        self.DATABASE = models.database_connect()

    def open_socket(self):
        """
        Initialization socket
        """
        try:
            self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.SERVER.bind((self.SERVER_IP, self.SERVER_PORT))
            self.SERVER.listen(self.MAX_USERS)
        except Exception as e:
            print("\nNie udało się utworzyć gniazda.", str(e))
            sys.exit(1)
        print("\nUtworzono gniazdo...")
        return self.SERVER

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
            chan_list = ','.join([i.name for i in self.DATABASE.query(models.Channel).all()])
            return "CHANNELS " + chan_list

        elif comm == "JOIN":
            """
            Request for join channel
            example: JOIN name password
            """
            if len(params_list)<2:
                return "ERROR channel name or password not given"

            channel = self.DATABASE.query(models.Channel).filter_by(name=params_list[0]).first()
            if channel is None:
                return "ERROR channel does not exists"
            if params_list[1] == channel.password:  # CHECK PASSWORD: TODO encryption ???
                user_obj.channel_id = channel.id  # changing channel
                self.DATABASE.commit()
                return "JOINED"
            else:
                return "NOT_JOINED"

        elif comm == "ASK_CHAN_USERS":
            """
            Ask abount users on the channel
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
            tmp = self.DATABASE.query(models.User).filter_by(id=user_obj.id).first()
            self.DATABASE.delete(tmp)
            self.DATABASE.commit()
            return "DISCONNECTED"

        else:
            print("Unknow command:", comm)
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
            print("Timeout exceeded:", e)
            return "Timeout exceeded", user_id.id
        client.settimeout(None)
        comm = data.decode('utf-8').split(" ")[0]
        params_list = data.decode('utf-8').split(" ")[1:]

        if comm == "CONNECT":
            """
            Connect to server with nick
            example: CONNECT name
            """
            if len(params_list)<1:
                return "ERROR no nick given", user_id.id

            nick = params_list[0]

            if self.DATABASE.query(models.User).filter_by(nick=nick).first() is not None or\
                self.DATABASE.query(models.Black_Nick).filter_by(nick=nick).first() is not None:
                """
                nick is busy or blocked
                """
                return "NOT_CONNECTED", user_id.id

            try:
                self.DATABASE.add(models.User(nick, ip))
                self.DATABASE.commit()
                user_id = self.DATABASE.query(models.User).filter_by(nick=nick).first()
                return "CONNECTED", user_id.id
            except:
                self.DATABASE.rollback()
                return "ERROR database integrity error", user_id.id
        else:
            print("Please login first")
            return "Please login first", user_id.id


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

        while self.THREADS_LOCK:
            try:
                data = client.recv(self.SIZE_OF_BUFFER)
                if data:
                    comm = data.decode('utf-8').split(" ")[0]
                    params_list = data.decode('utf-8').split(" ")[1:]
                    response = self.commands(comm, params_list, user_obj)
                    client.send(response.encode('utf-8'))  # send response to client
                    if response == "DISCONNECTED":
                        client.close()
                        self.DATABASE.close()  # close database connection for this thread
                        print("Klient", ip, "rozłączył się")
                        return
                else:
                    client.close()
                    self.DATABASE.close()  # close database connection for this thread
                    print("Klient", ip, "zerwał połączenie")
                    return
            except Exception as e:
                client.close()
                self.DATABASE.close()  # close database connection for this thread
                print("\nManagement_connection error: ", str(e))
                return


    def run(self):
        """
        Listen to new connection and run threads for them.
        """
        self.open_socket()
        while True:
            try:
                client, address = self.SERVER.accept()
                if self.DATABASE.query(models.Black_IP).filter_by(ip=address[0]).first() is not None:
                    client.close()
                    continue
                print("Nowe połączenie: ", address[0])
                t=threading.Thread(target=self.management_connection, args = (client,))
                t.start()
            except KeyboardInterrupt:
                self.THREADS_LOCK = False
                self.DATABASE.close()
                print("\nClosing server...")
                return


if __name__ == "__main__": 
    s = Server() 
    s.run()