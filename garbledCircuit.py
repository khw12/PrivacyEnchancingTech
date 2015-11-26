from random import *
from math import *
import numpy as np

AES_KEY_LENGTH = 128

# assume wire 1 and wire 2 already populated with input A and B.
def evaluate_garbled_circuit(wires, gates, C, D, output_1_p, output_2_p):
	#possible_output = np.zeros((pow(2, num_inputs), num_inputs + num_outputs))
	#for i in range(int(pow(2, num_inputs))):
	#	for j in range(num_inputs, 0, -1):
	#		possible_output[i, num_inputs - j] = fmod(floor(i / pow(2, j-1)), 2)

	num_wires = len(wires)
	num_gates = len(gates)

	# populate wire 3 and 4 with input C and D
	wires[2].set_value(C ^ wires[2].p)
	wires[2].set_decryption_key(wires[2].key[C])
	wires[3].set_value(D ^ wires[3].p)
	wires[3].set_decryption_key(wires[3].key[D])
	for i in range(num_gates):
		current_gate = gates[i]
		garbled_table = current_gate.garbled_table
		if (current_gate.gate_type == 'NOT'):
			encrypted_key = garbled_table[current_gate.input_wires[0].value, 1]
			encrypted_value = garbled_table[current_gate.input_wires[0].value, 2]
			current_gate.output_wire.set_decryption_key(decrypt(current_gate.input_wires[0].decryption_key, encrypted_key))
			current_gate.output_wire.set_value(decrypt(current_gate.input_wires[0].decryption_key, encrypted_value))
		else:
			for j in range(len(garbled_table)):
				if (garbled_table[j,0] == current_gate.input_wires[0].value & garbled_table[j,1] == current_gate,input_wires[1].value):
					encrypted_key = garbled_table[j, 2]
					encrypted_value = garbled_table[j, 3]
					break
			current_gate.output_wire.set_decryption_key(decrypt(current_gate.input_wires[0].decryption_key, 
				decrypt(current_gate.input_wires[1].decryption_key, encrypted_key)))
			current_gate.output_wire.set_value(decrypt(current_gate.input_wires[0].decryption_key, 
				decrypt(current_gate.input_wires[1].decryption_key, encrypted_value)))

	# extract value from output wires
	output_1 = wires[num_wires-2]
	output_2 = wires[num_wires-1]
	value_output_1 = output_1.value ^ output_1.p[output_1_p]
	value_output_2 = output_2.value ^ output_2.p[output_2_p]
	return([value_output_1, value_output_2])

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

	def set_decryption_key(self, key):
		self.decryption_key = key

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