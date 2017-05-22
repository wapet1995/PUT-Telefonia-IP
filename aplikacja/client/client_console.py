# -*- coding: utf-8 -*-

import socket
import sys



class Client:
	def __init__(self):
		self.SIZE_OF_BUFFER = 1024
		self.MY_NAME = None
		self.MY_IP_ADDRESS = None
		self.SERVER_IP_ADDRESS = None
		self.SERVER_PORT = None
		self.CONNECTION = None

	def login(self, nick):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.SERVER_IP_ADDRESS, self.SERVER_PORT))
		except Exception as e:
			print("\nNie udało się nawiązać połączenia.", str(e))
			return False

		s.settimeout(10.0)
		# send nick
		s.send(nick.encode('utf-8'))
		try:
			response = s.recv(self.SIZE_OF_BUFFER)
		except:
			print("Connection error")
			return False

		if response.decode('utf-8') == "CONNECTED":
			self.MY_NAME = nick
			self.CONNECTION = s
			return True