from random import *
from math import *
import numpy as np
import itertools
range = lambda stop: iter(itertools.count().next, stop)

"""
gates = {G1 ... G10}
wires = {W1 ... W20}
"""
AES_KEY_LENGTH = 128

def evaluate_garbled_circuit(wires, gates, C, D):
	#possible_output = np.zeros((pow(2, num_inputs), num_inputs + num_outputs))
	#for i in range(int(pow(2, num_inputs))):
	#	for j in range(num_inputs, 0, -1):
	#		possible_output[i, num_inputs - j] = fmod(floor(i / pow(2, j-1)), 2)

	num_wires = len(wires)
	num_gates = len(gates)
	# random AES keys
	#wire_keys = [[getrandbits(AES_KEY_LENGTH) for i in range(num_wires)] for j in range(2)]
	# random p[w] value
	#wire_p = [randint(0,1) for i in range(num_wires)]
	# initialise input values of all wires to 0
	#wire_values = np.zeros(num_wires)


def encrypt(key, plaintext):
	ciphertext = plaintext
	return(ciphertext)

def decrypt(key, ciphertext):
	plaintext = ciphertext
	return(plaintext)

class Wire:
	def __init__(self):
		self.key = [getrandbits(AES_KEY_LENGTH) for i in range(2)]
		self.p = randint(0,1)

	def set_value(self, val):
		self.value = val

class Gate:
	def __init__(self, gate_type, gate_func, input_wires, output_wire):
		self.gate_type = gate_type
		self.gate_func = gate_func
		self.input_wires = input_wires
		self.output_wire = output_wire
		self.generate_garbled_table()

	def generate_garbled_table(self):
		if (self.gate_type == 'NOT'):
			self.garbled_table = np.zeros((2, 3))
			self.garbled_table[0, 0] = int(0)
			self.garbled_table[1, 0] = int(1) 
		else:
			self.garbled_table = np.zeros((4, 4))
			for i in range(4):
				self.garbled_table[i, 0] = int(floor(i / 2))
				self.garbled_table[i, 1] = int(fmod(j, 2))
		for i in range(len(self.garbled_table)):
			x = int(self.garbled_table[i][0]) ^ self.input_wires[0].p
			if (self.gate_type == 'NOT'):
				z = self.gate_func(x)
				t = z ^ self.output_wire.p
				self.garbled_table[i, 1] = encrypt(self.input_wires[0].key[x], self.output_wire.key[z])
				self.garbled_table[i, 2] = encrypt(self.input_wires[0].key[x], t)
			else:
				y = self.garbled_table[i][1] ^ self.input_wires[1].p
				z = self.gate_func(x, y)
				t = z ^ self.output_wire.p
				self.garbled_table[i, 2] = self.encrypt_helper(x, y, self.output_wire.key[z])
				self.garbled_table[i, 3] = self.encrypt_helper(x, y, t)

	def encrypt_helper(self, x, y, text):
		return(encrypt(self.input_wires[0].key[x], encrypt(self.input_wires[1].key[y], text)))