import secrets
from service import is_prime, nsd, find_reverse


class KeyPair:
    """This class identifies single public and private key pair"""
    def __init__(self):
        self.sk, self.pk = self.genKeyPair()

    def genKeyPair(self):
        """This function generates random private and public keys pair.p and q are chosen in range [0, 2000]"""

        # Generating p and q
        while True:
            p = secrets.randbelow(2000)
            if is_prime(p):
                break
        while True:
            q = secrets.randbelow(2000)
            if is_prime(q):
                break

        n = p * q
        e_func = (p - 1) * (q - 1)
        seq = list(range(2, e_func - 1))

        # Generating e
        while True:
            e = secrets.choice(seq)
            if nsd(e, e_func) == 1:
                break

        # finding d
        d = find_reverse(e, 1, e_func)

        # key pair
        pk = (e, n)
        sk = (d, n)
        return sk, pk

    def __repr__(self):
        """String representation of key pair"""
        return f"Secret key is: {self.sk}\nPublic key is: {self.pk}"


class Signature:
    """This class contains methods for digital signing and verifying digital sign"""
    @staticmethod
    def sign(sk, msg):
        d = sk[0]
        n = sk[1]
        S = (msg ** d) % n
        return S

    @staticmethod
    def verifySig(sig, pk, msg):
        e = pk[0]
        n = pk[1]
        return msg == (sig ** e) % n


class Account:
    """This class determines system's user account"""
    acc_id_counter = 1 # this variable increments whenever new account is created

    def __init__(self):
        self.accountID = Account.acc_id_counter
        Account.acc_id_counter += 1
        self.wallet = [KeyPair()]
        self.balance = 0

    def genAccount(self):
        return Account()

    def addKeyPairToWallet(self):
        self.wallet.append(KeyPair())

    def updateBalance(self, value: int):
        self.balance = value

    def createPaymentOp(self, pay_to_acc, amount, key_ix):
        ... # this method will be updated after adding Operation class

    def getBalance(self):
        return self.balance

    def printBalance(self):
        print(self.balance)

    def signData(self, data, key_ix):
        kp = self.wallet[key_ix]
        S = Signature.sign(kp.sk, data)
        return S

    def __repr__(self):
        """String representation of account"""
        return f"Account id: {self.accountID}\nAccount balance: {self.balance}"

