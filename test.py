import hashlib, binascii

dk = hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000)
print(binascii.hexlify(dk))
