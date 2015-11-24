from random import *

"""
gates = {G1 ... G10}
wires = {W1 ... W20}
"""

def evaluate_garbled_circuit():
	# Let keys be integer value between 1 and 1000
	wireKeys = [[randint(1, 1000) for i in range(20)] for j in range(2)]
	# random p[w] value
	pWires = [randint(0,1) for i in range(20)]
	print wireKeys

def encrypt(key, plaintext):
	ciphertext = plaintext
	return(ciphertext)

def decrypt(key, ciphertext):
	plaintext = ciphertext
	return(plaintext)