# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Simul crypto lib """

class aes:
	""" Aes crypto class """
	def __init__(self, key, mode = 1):
		self.key = key

	def encrypt(self, content):
		""" Encrypt data """
		try:
			from Cryptodome.Cipher import AES
			from Cryptodome        import Random
		except ImportError:
			from Crypto.Cipher import AES
			from Crypto        import Random

		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		result =  iv + cipher.encrypt(content)
		return result

	def decrypt(self, ciphertext):
		""" Decrypt data """
		try:
			from Cryptodome.Cipher import AES
		except ImportError:
			from Crypto.Cipher import AES

		iv = ciphertext[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		plaintext = cipher.decrypt(ciphertext[AES.block_size:])
		return plaintext
