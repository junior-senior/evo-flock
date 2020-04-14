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

    creatures = [num_creatures]
    predator = Predator
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
            self.speed: float = 0
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
            x: float = EvoFlock.random_float(1)
            y: float = EvoFlock.random_float(1)
            heading: float = EvoFlock.random_float(360)
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
        """This class defines the creatures or prey. It inherits from the Agent class."""
        def __init__(self):
            self.eyes = [EvoFlock.num_eyes]
            self.predator_in_eye: int = 0
            self.genotype = [EvoFlock.genotype_length]
            self.speed = super().speed

            [EvoFlock.random_float(2) for genomes in self.genotype]

        def which_eye(self, x: float, y: float) -> int:
            """This method is used to determine which eye the predator is seen in for this creature"""
            dx: float = x - self.x_position
            dx += 1 if dx < -0.5 else dx
            dx -= 1 if dx > 0.5 else dx

            dy: float = y - self.y_position
            dy += 1 if dy < -0.5 else dy
            dy -= 1 if dy > 0.5 else dy

            angle = math.degrees(math.atan2(-dy, dx)) - self.heading
            dh: float = super().wrap_360(angle)
            return int(((dh * EvoFlock.num_eyes) / 360))

        def update_eyes(self):
            """This method updates what each creature sees in each eye"""
            self.predator_in_eye = self.which_eye(predator.x, predator.y)
            [1 if eye is self.eyes[self.predator_in_eye] else 1 for eye in self.eyes]
            for c in range(0, EvoFlock.num_creatures):
                if EvoFlock.creatures[c] is not self:
                    self.eyes[self.which_eye(EvoFlock.creatures[c].x_position, EvoFlock.creatures[c].y_position)] += 1

        def update_heading(self):
            """This method updates the heading for the creature"""
            output: float = 0
            for i in range(EvoFlock.num_eyes):
                output += self.genotype[i + (self.predator_in_eye * EvoFlock.num_eyes)] * self.eyes[i]
            new_heading: float = self.heading + output
            self.heading = self.wrap_360(new_heading)

        def crossover(self, parent_a: int, parent_b: int):
            cutpoint: int = EvoFlock.rng(EvoFlock.genotype_length - 1) + 1
            for i in range(EvoFlock.genotype_length):
                 if i < cutpoint:
                     self.genotype[i] = EvoFlock.creatures[parent_a].genotype[i]
                 else:
                     self.genotype[i] = EvoFlock.creatures[parent_b].genotype[i]

        def mutate(self):
            for i in range(EvoFlock.genotype_length):
                if random.random > 0.9:
                    mutation: float = random.random
                    if random.random < 0.5:
                        mutation = - mutation
                    self.genotype[i] = mutation

    class Predator(Agent):
        pass
