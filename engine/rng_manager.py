import random
import secrets

class RNGManager:
    def __init__(self, seed: int = None):
        if seed is None:
            seed = secrets.randbits(32)
        self.seed = seed
        self.rng = random.Random(seed)

    def get_int(self, a: int, b: int) -> int:
        return self.rng.randint(a, b)

    def get_float(self) -> float:
        return self.rng.random()

    def choice(self, seq):
        return self.rng.choice(seq)

    def shuffle(self, seq):
        self.rng.shuffle(seq)

    def reseed(self, seed: int):
        self.seed = seed
        self.rng.seed(seed)
