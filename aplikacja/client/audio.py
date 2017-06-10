# -*- coding: utf-8 -*-

import pyaudio

class Audio:
	def __init__(self, sock):
		self.sock = sock
		self.CHUNK = 512
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 44100

		self.p = pyaudio.PyAudio()
		self.stream_input = self.p.open(format = self.FORMAT,
							channels = self.CHANNELS,
							rate = self.RATE,
							input = True,
							frames_per_buffer = self.CHUNK,
							stream_callback = call_input)

		self.stream_output = self.p.open(format = self.FORMAT,
							channels = self.CHANNELS,
							rate = self.RATE,
							output=True,
							frames_per_buffer = self.CHUNK,
							stream_callback = call_output)

	def call_input(in_data, frame_count, time_info, status):
	    return (data, pyaudio.paContinue)

	def record(self):
		return self.stream.read(self.CHUNK)

	def play(self, data):
		self.stream.write(data)

	def exit(self):
		self.stream.close()
		self.p.terminate()

