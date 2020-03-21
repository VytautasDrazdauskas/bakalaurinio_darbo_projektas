import pyaes, pbkdf2, binascii, os, secrets, io
import service.helpers.loadConfig as config

#per mqtt kanala geriau siusti visa vektoriu jsonu
class IV(pyaes.Counter):
    def __init__(self, iv):
        self._counter = iv

class AESCipher(object):
    #inicializuojamas objektas su keliu iki raktu direktorijos
    def __init__(self):
        self.path = config.keys.directory

    # uzsifruojama ir konvertuojama i hex
    def encrypt(self, plain_text, key):
        try:
            iv = secrets.randbits(256)
            iv_vector = pyaes.Counter(iv)
            aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
            data = aes.encrypt(plain_text + ";")
            hex = binascii.hexlify(data)
            return {'data':hex.decode("ASCII"),'iv':iv_vector.value}
        except Exception as ex:
            raise

    #atsifravimas is hex binary arba hex str
    def decrypt(self, enc, key):
        try:
            iv = IV(enc['iv'])
            aes = pyaes.AESModeOfOperationCTR(key, iv)
            result = aes.decrypt(binascii.unhexlify(enc['data'])).decode('utf-8')
            return result.split(';')[0]  #grazinam viska iki terminatoriaus
        except Exception as ex:
            return None

    #generuojamas AES raktas naudojant slaptazodi
    def generate_key(self, password):
        try:
            passwordSalt = os.urandom(16)
            return pbkdf2.PBKDF2(password, passwordSalt).read(32)
        except Exception as ex:
            raise

    #rakto issaugojimas i binary faila
    def save_key(self, key, filename):
        try:
            file = open(self.path + filename ,"wb")
            file.write(binascii.hexlify(key))
            file.close
        except Exception as ex:
            raise

    #rakto uzkrovimas is binary failo
    def load_key(self, filename):
        try:    
            if (os.path.exists(self.path + filename)):        
                file = open(self.path + filename,"rb")
                key = binascii.unhexlify(file.read())
                file.close
                return key
            else:
                return None
        except Exception as ex:
            raise