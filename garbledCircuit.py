from random import *
from math import *
from Crypto.Cipher import AES
import numpy as np
import string

AES_KEY_LENGTH = 16

def generate_all_possible_output():
	possible_output = np.zeros([16, 6], dtype=int)
	for i in range(16):
		for j in range(4, 0, -1):
			possible_output[i, 4-j] = int(fmod(floor(i / pow(2, j-1)), 2))
		[wires, gates] = generate_max_garbled_circuit(possible_output[i, 0], possible_output[i, 1])
		[output1, output2] = evaluate_garbled_circuit(wires, gates, possible_output[i, 2], possible_output[i, 3])
		possible_output[i, 4] = output1
		possible_output[i, 5] = output2
	return(possible_output)


# assume wire 1 and wire 2 already populated with input A and B.
def evaluate_garbled_circuit(wires, gates, C, D):
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
			encrypted_key = garbled_table[current_gate.input_wires[0].value][0]
			encrypted_value = garbled_table[current_gate.input_wires[0].value][1]
			current_gate.output_wire.set_decryption_key(decrypt(current_gate.input_wires[0].decryption_key, encrypted_key))
			current_gate.output_wire.set_value(decrypt(current_gate.input_wires[0].decryption_key, encrypted_value))
		else:
			encrypted_key = garbled_table[(current_gate.input_wires[0].value, current_gate.input_wires[1].value)][0]
			encrypted_value = garbled_table[(current_gate.input_wires[0].value, current_gate.input_wires[1].value)][1]
			current_gate.output_wire.set_decryption_key(decrypt(current_gate.input_wires[0].decryption_key, 
				decrypt(current_gate.input_wires[1].decryption_key, encrypted_key)))
			current_gate.output_wire.set_value(decrypt(current_gate.input_wires[0].decryption_key, 
				decrypt(current_gate.input_wires[1].decryption_key, encrypted_value)))

	# extract value from output wires
	output_1 = wires[num_wires-2]
	output_2 = wires[num_wires-1]
	value_output_1 = int(output_1.value) ^ output_1.p
	value_output_2 = int(output_2.value) ^ output_2.p
	return([value_output_1, value_output_2])

def generate_max_garbled_circuit(A, B):
	wires = [Wire() for i in range(14)]
	# populate the input wire with A and B
	wires[0].set_value(A ^ wires[0].p)
	wires[0].set_decryption_key(wires[0].key[A])
	wires[1].set_value(B ^ wires[1].p)
	wires[1].set_decryption_key(wires[1].key[B])

	gate1 = Gate('NOT', not_gate_function, [wires[0]], wires[4])
	gate2 = Gate('NOT', not_gate_function, [wires[2]], wires[5])
	gate3 = Gate('AND', and_gate_function, [wires[0], wires[1]], wires[6])
	gate4 = Gate('AND', and_gate_function, [wires[1], wires[5]], wires[7])
	gate5 = Gate('AND', and_gate_function, [wires[2], wires[3]], wires[8])
	gate6 = Gate('AND', and_gate_function, [wires[3], wires[4]], wires[9])
	gate7 = Gate('OR', or_gate_function, [wires[6], wires[7]], wires[10])
	gate8 = Gate('OR', or_gate_function, [wires[8], wires[9]], wires[11])
	gate9 = Gate('OR', or_gate_function, [wires[0], wires[2]], wires[12])
	gate10 = Gate('OR', or_gate_function, [wires[10], wires[11]], wires[13])
	gates = [gate1, gate2, gate3, gate4, gate5, gate6, gate7, gate8, gate9, gate10]

	return([wires, gates])

def encrypt(key, plaintext):
	print plaintext
	aes = AES.new(key, AES.MODE_CBC, key)
	if (len(str(plaintext)) == 1):
		plaintext = "000000000000000" + str(plaintext)
	ciphertext = aes.encrypt(str(plaintext))
	print ciphertext
	return(ciphertext)

def decrypt(key, ciphertext):
	plaintext = ciphertext
	return(plaintext)

def not_gate_function(input):
	return(abs(1-input))

def and_gate_function(input1, input2):
	return(input1 & input2)

def or_gate_function(input1, input2):
	return(input1 | input2)

class Wire:
	def __init__(self):
		self.key = [(''.join(choice(string.lowercase) for x in range(AES_KEY_LENGTH))) for i in range(2)]
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
			self.garbled_table = {0: ["" for i in range(2)], 1: ["" for i in range(2)]}
		else:
			self.garbled_table = {(0,0): ["" for i in range(2)], (0,1): ["" for i in range(2)],
				(1,0): ["" for i in range(2)], (1,1): ["" for i in range(2)]}
		for i in range(len(self.garbled_table)):
			if (self.gate_type == 'NOT'):
				x = int(self.garbled_table.keys()[i]) ^ self.input_wires[0].p
				z = self.gate_func(x)
				t = z ^ self.output_wire.p
				self.garbled_table[i][0] = encrypt(self.input_wires[0].key[x], self.output_wire.key[z])
				self.garbled_table[i][1] = encrypt(self.input_wires[0].key[x], t)
			else:
				x = int(self.garbled_table.keys()[i][0]) ^ self.input_wires[0].p
				y = int(self.garbled_table.keys()[i][1]) ^ self.input_wires[1].p
				z = self.gate_func(x, y)
				t = z ^ self.output_wire.p
				self.garbled_table[self.garbled_table.keys()[i]][0] = self.encrypt_helper(x, y, self.output_wire.key[z])
				self.garbled_table[self.garbled_table.keys()[i]][1] = self.encrypt_helper(x, y, t)

	def encrypt_helper(self, x, y, text):
		return(encrypt(self.input_wires[0].key[x], encrypt(self.input_wires[1].key[y], text)))

def main():
	output = generate_all_possible_output()
	print output
main()