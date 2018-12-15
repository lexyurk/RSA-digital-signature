from random import randrange

from primes import generate_large_prime, gcd, extended_gcd, is_prime


class Encryption:
    """
    Generating keys, making digital signature and checking signature on validness
    """

    def __init__(self):
        self.keys = dict()
        self.is_all_keys = False

    def set_keys(self, key_size=1024, **kwargs):
        """
        Setting up public and private keys
        :param key_size: size of p and q (in bits)
        :param kwargs: dict that includes keys
        :return: keys
        """
        if 'p' in kwargs:
            if is_prime(kwargs['p']):
                self.keys['p'] = kwargs['p']
            else:
                raise KeyError("P key is not prime.")
        else:
            self.keys['p'] = generate_large_prime(key_size)

        if 'q' in kwargs:
            if is_prime(kwargs['q']):
                self.keys['q'] = kwargs['q']
            else:
                raise KeyError("Q key is not prime.")
        else:
            self.keys['q'] = generate_large_prime(key_size)

        self.keys['n'] = self.keys['p'] * self.keys['q']
        self.keys['fn'] = (self.keys['p'] - 1) * (self.keys['q'] - 1)

        return self.keys

    @staticmethod
    def check_public_private_key(key, fn):
        """
        Checking public or private key
        :param key: key to check (public or private)
        :param fn: Result of Euler's function
        :return: key if key is valid
        """

        class KeyInputError(Exception):
            pass

        if gcd(key, fn) == 1:
            return key
        raise KeyInputError("Entered key is not valid.")

    def check_keys(self, keys):
        """
        Checking all keys if they are valid
        :param keys: dict of keys to check
        :return: True if all keys are valid, else False
        """
        keys_to_check = ['p', 'q', 'n', 'fn', 'e', 'd']
        self.is_all_keys = True
        for key in keys_to_check:
            if key not in keys.keys():
                self.is_all_keys = False
        if not self.is_all_keys or not self.check_public_private_key(keys['e'], keys['fn']) \
                or not self.check_public_private_key(keys['d'], keys['fn']):
            self.is_all_keys = False
            return False
        return True

    def generate_keys(self, _euler=0, _public_key=0, _private_key=0, key_size=1024):
        """
        Generating public / private keys
        :param _euler: result of euler function
        :param _public_key: public key value
        :param _private_key: private key value
        :param key_size: size of key if it's not generated (in bits)
        :return: dictionary, that includes public ('e') and private ('d') keys
        """
        if not _euler:
            try:
                _euler = (self.keys['p'] - 1) * (self.keys['q'] - 1)
            except Exception:
                raise KeyError("P and Q keys are not defined.")
        # If all keys are generated
        if _public_key and _private_key:
            return {'e': _public_key, 'd': _private_key}
        # if only public key is generated
        elif _public_key:
            _private_key = extended_gcd(_public_key, _euler)
            _private_key = _private_key[1] if _private_key[1] > 0 else _private_key[2]
        # if only private key is generated
        elif _private_key:
            _public_key = extended_gcd(_private_key, _euler)[1]
        # if no keys were generated
        # generating one key and recursively call function with generated key
        else:
            while True:
                _public_key = randrange(1, key_size)
                if gcd(_public_key, _euler) == 1:
                    return self.generate_keys(_euler, _public_key)
        return {'e': _public_key, 'd': _private_key}

    def generate_key(self, key, key_size=1024):
        """
        Generating large prime key (p or q) and setting this key up
        :param key: string, includes 'p' or 'q'
        :param key_size: size of key to generate (in bits), default 1024
        :return: generated key
        """
        self.keys[key] = generate_large_prime(key_size)
        return self.keys[key]

    @staticmethod
    def _open_file_binary(filename):
        """
        Reading file byte to byte
        :param filename: path to file to read
        :return: generator of file bytes as integer values
        """
        for _byte in open(filename, 'rb').read():
            yield _byte

    def get_hash(self, file_name, _hash=100):
        """
        Cointing hash-function of all file
        :param file_name: filename of file to count hash
        :param _hash: start hash (default 100)
        :return: value of hash
        """
        if not self.check_keys(self.keys):
            raise KeyError("Keys are not valid.")
        file_bytes = self._open_file_binary(file_name)
        for file_byte in file_bytes:
            _hash = (_hash + file_byte) % self.keys['n']
        return _hash

    def get_signature_private(self, filename):
        """
        Generating file signature using private key
        :param filename: filename to get hash
        :return: Signature of file
        """
        if not self.check_keys(self.keys):
            raise KeyError("Keys are not valid.")
        hashed_message = self.get_hash(filename)
        signature = pow(hashed_message, self.keys['d'], self.keys['n'])
        return signature

    def is_signature_valid(self, filename, signature, _public_key):
        """
        Checking file signature
        :param filename: Name of file to check signature
        :param signature: Signature to check
        :param _public_key: public key to check function
        :return: True if valid, else False. Also returns calculated hash and signature
        """
        message_hash_recovered = pow(signature, _public_key['e'], _public_key['n'])
        message_hash = self.get_hash(filename)
        if message_hash == message_hash_recovered:
            return [True, message_hash_recovered, message_hash]
        return [False, message_hash_recovered, message_hash]


if __name__ == '__main__':
    public_key = 43
    euler = 288
    private_key = 3
    while True:
        if ((public_key % euler) * (private_key % euler)) % euler == 1:
            print(private_key)
            break
        private_key += 1
    print(extended_gcd(public_key, euler)[1])
