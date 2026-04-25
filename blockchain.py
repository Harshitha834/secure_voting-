import hashlib
import datetime

class Block:
    def __init__(self, index, vote, prev_hash):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.vote = vote
        self.prev_hash = prev_hash
        self.hash = self.create_hash()

    def create_hash(self):
        data = f"{self.index}{self.timestamp}{self.vote}{self.prev_hash}"
        return hashlib.sha256(data.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis()]

    def create_genesis(self):
        return Block(0, "Genesis", "0")

    def add_block(self, vote):
        prev = self.chain[-1]
        new_block = Block(len(self.chain), vote, prev.hash)
        self.chain.append(new_block)

    # 🔐 Tamper detection
    def is_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]

            if current.hash != current.create_hash():
                return False

            if current.prev_hash != prev.hash:
                return False

        return True


blockchain = Blockchain()