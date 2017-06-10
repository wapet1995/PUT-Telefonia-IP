# -*- coding: utf-8 -*-

import pyaudio

class Audio:
	def __init__(self):
		self.CHUNK = 512
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 44100

		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format = self.FORMAT,
							channels = self.CHANNELS,
							rate = self.RATE,
							input = True,
							output=True,
							frames_per_buffer = self.CHUNK)
		#self.stream.start_stream()


	def record(self):
		return self.stream.read(self.CHUNK)

	def play(self, data):
		self.stream.write(data)

	def exit(self):
		self.stream.close()
		self.p.terminate()

