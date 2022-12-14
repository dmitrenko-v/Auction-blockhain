import hashlib
import secrets
from service import is_prime, nsd, find_reverse

data = 5
class Item:
    """This class defines item on auction"""
    item_id_counter = 1

    def __init__(self, initial_price, name):
        self.price = initial_price
        self.id = Item.item_id_counter
        Item.item_id_counter += 1
        self.name = name
        self.prev_price = self.price

    def correct_bid(self, new_price):
        return new_price > self.prev_price

    def new_price(self, price):
        if self.correct_bid(price):
            self.prev_price, self.price = self.price, price

    def __repr__(self):
        """String representation of item"""
        return f"Name: {self.name}\nPrevious price: {self.prev_price}\nCurrent price: {self.price}\nItem id: {self.id}"

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
    def sign(sk):
        d = sk[0]
        n = sk[1]
        S = (data ** d) % n
        return S

    @staticmethod
    def verifySig(sig, pk):
        e = pk[0]
        n = pk[1]
        return data == (sig ** e) % n


class Account:
    """This class determines system's user account"""
    acc_id_counter = 1 # this variable increments whenever new account is created

    def __init__(self):
        self.accountID = Account.acc_id_counter
        Account.acc_id_counter += 1
        self.wallet = [KeyPair()]
        self.balance = 0

    def addKeyPairToWallet(self):
        self.wallet.append(KeyPair())

    def updateBalance(self, value: int):
        self.balance = value

    def createPaymentOp(self, amount, key_ix, item):
        """data: data for digital signature"""
        return Operation(self, amount, self.signData(key_ix), item)

    def getBalance(self):
        return self.balance

    def printBalance(self):
        print(self.balance)

    def signData(self, key_ix):
        kp = self.wallet[key_ix]
        S = Signature.sign(kp.sk)
        return S

    def __repr__(self):
        """String representation of account"""
        return f"Account id: {self.accountID}\nAccount balance: {self.balance}"


class Operation:
    """This class describes single operation"""
    operation_id = 1

    def __init__(self, sender: Account, amount, sig, item: Item):
        self.id = Operation.operation_id
        Operation.operation_id += 1
        self.sender = sender
        self.amount = amount
        self.sig = sig
        self.item = item

    @staticmethod
    def verifyOperation(op, key_ix):
        """data: data to verify signature
           key_ix: key index in account's key wallet to verify signature"""
        return op.amount <= op.sender.balance and Signature.verifySig(op.sig, op.sender.wallet[key_ix].pk) and op.item.correct_bid(op.amount)

    def __repr__(self):
        """String representation of operation"""
        return f"Operation id:{self.id}\nOperation amount: {self.amount}\n{str(self.sender)}\n{str(self.item)}"


class Transaction:
    transaction_id = 1

    def __init__(self, set_of_operations: [Operation]):
        self.id = Transaction.transaction_id
        Transaction.transaction_id += 1
        self.set_of_operations = set_of_operations


    def __repr__(self):
        """String representation of operation"""
        return f"Transaction id: {self.id}\nOperations list:{self.set_of_operations}\n"


class Block:
    block_id = b"0"
    """This class defines block in blockchain"""
    def __init__(self, prevHash, setOfTransactions: [Transaction]):
        id = hashlib.sha1()
        id.update(Block.block_id)
        self.blockId = id.hexdigest()
        Block.block_id += b"0"
        self.prevHash = prevHash
        self.setOfTransactions = setOfTransactions

    def __repr__(self):
        return f"Block id: {self.blockId}\nPrevious block hash: {self.prevHash}\nTransactions: {self.setOfTransactions}"


class Blockchain:
    faucetCoins = 5

    def __init__(self):
        self.coinDatabase = dict()
        self.blockHistory = []
        self.txDatabase = []

    def initBlockchain(self):
        """This function creating genesis block in blockchain(initializing blockchain)"""
        GenesisBlock = Block("0"*40, [])
        self.blockHistory.append(GenesisBlock)

    def validateBlock(self, block: Block):
        """This function validates/not validates given block and add/doesn't add it to blockchain"""
        if block.prevHash == self.blockHistory[-1].blockId and len(block.setOfTransactions) <= 7:
            for tr in block.setOfTransactions:
                if block.setOfTransactions.count(tr) > 1:
                    print("There are conflicting transactions")
                    return False
                if tr in self.txDatabase:
                    print("Block is invalid. Transaction is already in blockchain")
                    return False
        else:
            print("Block hash didn't match last block hash or there are too many transactions")
            return False

        local_story = dict()

        # conflicting transactions detection block
        for tr in block.setOfTransactions:
            for op in tr.set_of_operations:
                if op.sender not in local_story:
                    local_story[op.sender] = op.sender.balance - op.amount
                else:
                    local_story[op.sender] -= op.amount
                if not Operation.verifyOperation(op, 0):
                    print("Block is invalid.There are invalid transactions")
                    return False
            for acc in local_story:
                if local_story[acc] < 0:
                    print("Block is invalid.There are invalid transactions")
                    return False
        for acc in local_story:
            if local_story[acc] < 0:
                print("Block is invalid.There are invalid transactions")
                return False

        # if block is valid, then update coinDatabase and account balances
        for tr in block.setOfTransactions:
            for op in tr.set_of_operations:
                op.sender.balance -= op.amount
                op.item.new_price(op.amount)
                self.coinDatabase[op.sender] = op.sender.balance

        self.txDatabase.extend(block.setOfTransactions)
        self.blockHistory.append(block)
        print("Block is created")

    def getTokenFromFaucet(self):
        """This function gives every user of blockchain test tokens"""
        for acc in self.coinDatabase:
            self.coinDatabase[acc] += self.faucetCoins
            acc.balance += self.faucetCoins

    def getCoinDatabase(self):
        print(self.coinDatabase)

    def __repr__(self):
        return str(self.blockHistory)



