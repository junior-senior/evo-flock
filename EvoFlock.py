import random
import math

class EvoFlock:
    """EvoFlock is a simluation of a predator-prey scenario where the prey are subject to an Evolutionary Algorithm.
    Each time a prey is caught, a new one is produced via crossover and mutation."""
    counter: int = 0
    reproductions: int = 0

    # Creature Variables
    creature_speed: float = 0.01
    predator_speed: float = 0.015
    creature_diameter: float = 0.015
    num_creatures: int = 50
    num_eyes: int = 8
    genotype_length: int = num_eyes**2

    @staticmethod
    def rng(n: int):
        """Returns a random integer between 0 and n-1."""
        return random.randint(0, n)

    @staticmethod
    def random_float(d: float):
        """Returns a random double in the range [0, d)."""
        return d * random.uniform(0, d)

    @staticmethod
    def random_gaussian(d: float):
        """Returns a Gaussian-random double in the rand, mean 0, stdev d."""
        return d * random.gauss(0, d)

    @staticmethod
    def cos_degree(h: float):
        """Gets the cos of an angle in degrees."""
        return math.cos(math.radians(h))

    @staticmethod
    def sin_degrees(h: float):
        """Gets the sin of an angle in degrees."""
        return math.sin(math.radians(h))

    class Agent:
        """Class defining the base attributes of an Agent in the suimulation. Creature and Predator will inherit from
        this class."""

        def __init__(self):
            self.x_position: float
            self.y_position: float
            self.speed: float
            self.heading: float
            self.x_position, self.y_position, self.heading = self.randomize_position_and_heading()

        @staticmethod
        def wrap_360(h: float):
            """If the agent exceeds 0 or 360 degrees, need to wrap the rotation"""
            h += 360 if h < 0 else h
            h -= 360 if h > 360 else h
            return h

        @staticmethod
        def randomize_position_and_heading():
            """Randomises the position and heading of the Agent on Initialisation"""
            x = EvoFlock.random_float(1)
            y = EvoFlock.random_float(1)
            heading = EvoFlock.random_float(360)
            return x, y, heading

        def update_position(self):
            """Updates the position of the Agent"""
            self.x_position += EvoFlock.cos_degree(self.heading) * self.speed
            self.x_position += 1 if self.x_position < 1 else self.x_position
            self.x_position -= 1 if self.x_position > 1 else self.x_position

            self.y_position += EvoFlock.sin_degree(self.heading) * self.speed
            self.y_position += 1 if self.y_position < 1 else self.y_position
            self.y_position -= 1 if self.y_position > 1 else self.y_position

    class Creature(Agent):
