from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

async def generate_key():
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()

    private_key = private_key.exportKey().decode("utf-8")
    public_key = public_key.exportKey().decode("utf-8")
    return {"private_key": private_key, "public_key": public_key}

async def verify_app(private_key: str, public_key: str):
    word = "SMTSL"
    keyPub = RSA.importKey(public_key)
    public_cipher = Cipher_PKCS1_v1_5.new(keyPub)
    public_secret_word = public_cipher.encrypt(word.encode())
    keyPrv = RSA.import_key(private_key)
    private_cipher = Cipher_PKCS1_v1_5.new(keyPrv)
    decrypt_word = private_cipher.decrypt(public_secret_word, None).decode()
    return word == decrypt_word
