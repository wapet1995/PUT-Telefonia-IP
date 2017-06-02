# -*- coding: utf-8 -*-

import pyaudio

class Audio:
	def __init__(self):
		self.CHUNK = 1024
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 10240

		# recording voice
		self.p_speak = pyaudio.PyAudio()
		self.SPEAK = self.p_speak.open(format = self.FORMAT,
							channels = self.CHANNELS,
							rate = self.RATE,
							input = True,
							frames_per_buffer = self.CHUNK)
		
		# playing voice
		self.p_listen = pyaudio.PyAudio()
		self.LISTEN = self.p_listen.open(format = self.FORMAT,
							channels = self.CHANNELS,
							rate = self.RATE,
							output = True,
							frames_per_buffer = self.CHUNK)


	def record(self):
		data = self.SPEAK.read(self.CHUNK)
		return data

	def play(self, data):
		self.LISTEN.write(data)

	def exit(self):
		self.SPEAK.close()
		self.LISTEN.close()
		self.p_speak.terminate()
		self.p_listen.terminate()

