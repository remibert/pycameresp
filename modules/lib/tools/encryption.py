# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Encryption utility functions """
from binascii import hexlify, b2a_base64, a2b_base64
import hashlib
from tools import useful

Aes_ = None
def Aes(key, mode):
	""" AES object loaded on demand """
	global Aes_
	if Aes_ is None:
		import cryptolib
		Aes_ = cryptolib.aes
	if len(key) % 16 != 0:
		key = (key*16)[:16]
	return  Aes_(useful.tobytes(key), mode)

def encrypt(buffer, key):
	""" AES encryption of buffer """
	data = b2a_base64(buffer)
	data = data.rstrip()
	if len(data) % 16 != 0:
		data = data + b"="*(16-len(data)%16)
	return Aes(key,1).encrypt(useful.tobytes(data))

def decrypt(buffer, key):
	""" AES decryption of buffer """
	data = Aes(key, 1).decrypt(buffer)
	data = a2b_base64(useful.tobytes(data))
	return data

def gethash(password):
	""" Get the hash associated to the password """
	hash_ = hashlib.sha256()
	hash_.update(password)
	return hexlify(hash_.digest())