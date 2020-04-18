import random
import math
from decimal import Decimal
class EvoFlock:
    """EvoFlock is a simluation of a predator-prey scenario where the prey are subject to an Evolutionary Algorithm.
    Each time a prey is caught, a new one is produced via crossover and mutation."""
    def __init__(self):
        self.counter: int = 0
        self.reproductions: int = 0

        # Creature Variables
        self.creature_speed: float = 0.01
        self.predator_speed: float = 0.015
        self.creature_diameter: float = 0.15
        self.num_creatures: int = 50

        self.num_eyes: int = 8
        self.genotype_length: int = self.num_eyes**2

        self.creatures = []
        self.predator = Predator(self)

    @staticmethod
    def random_int(n: int):
        """Returns a random integer between 0 and n-1."""
        return random.randint(0, n)

    @staticmethod
    def random_float(d: float):
        """Returns a random double in the range [0, d)."""
        return random.uniform(0, d)

    @staticmethod
    def random_gaussian(d: float):
        """Returns a Gaussian-random double in the rand, mean 0, stdev d."""
        return d * random.gauss(0, d)

    @staticmethod
    def cos_degrees(h: float):
        """Gets the cos of an angle in degrees."""
        return

    @staticmethod
    def sin_degrees(h: float):
        """Gets the sin of an angle in degrees."""
        return


class Agent:
    """Class defining the base attributes of an Agent in the suimulation. Creature and Predator will inherit from
    this class."""

    def __init__(self):
        self.x_position: float
        self.y_position: float
        self.speed: float = 0
        self.heading: float
        self.randomize_position_and_heading()

    def wrap_360(self, h: float):
        """If the agent exceeds 0 or 360 degrees, need to wrap the rotation."""
        if h < 0:
            h += 360
        elif h > 360:
            h -= 360
        return round(h)

    def randomize_position_and_heading(self):
        """Randomises the position and heading of the Agent on Initialisation."""
        self.x_position: float = EvoFlock.random_float(1)
        self.y_position: float = EvoFlock.random_float(1)
        self.heading: float = self.wrap_360(EvoFlock.random_int(360))

    def update_position(self):
        """Updates the position of the Agent"""
        self.x_position += math.cos(math.radians(self.heading)) * self.speed
        self.x_position += 1 if self.x_position < 1 else self.x_position
        self.x_position -= 1 if self.x_position > 1 else self.x_position

        self.y_position += math.sin(math.radians(self.heading)) * self.speed
        self.y_position += 1 if self.y_position < 1 else self.y_position
        self.y_position -= 1 if self.y_position > 1 else self.y_position


class Creature(Agent):
    """This class defines the creatures or prey. It inherits from the Agent class."""
    def __init__(self, evoflock):
        super().__init__()
        self.eyes = [0] * evoflock.num_eyes
        self.predator_in_eye: int = 0
        self.genotype = [0.0] * evoflock.genotype_length

        for genome in range(len(self.genotype)):
            self.genotype[genome] = evoflock.random_float(2)-1

    def which_eye(self, x: float, y: float) -> int:
        """This method is used to determine which eye the predator is seen in for this creature."""
        dx: float = x - self.x_position
        dx += 1 if dx < -0.5 else dx
        dx -= 1 if dx > 0.5 else dx

        dy: float = y - self.y_position
        dy += 1 if dy < -0.5 else dy
        dy -= 1 if dy > 0.5 else dy

        angle = math.degrees(math.atan2(-dy, dx)) - self.heading
        dh: float = super().wrap_360(angle)
        return int(((dh * evoflock.num_eyes) / 360))

    def update_eyes(self):
        """This method updates what each creature sees in each eye."""
        self.predator_in_eye = self.which_eye(evoflock.predator.x_position, evoflock.predator.y_position)

        for eye in range(len(self.eyes)):
            self.eyes[eye] = 0

        for c in evoflock.creatures:
            if c is not self:
                self.eyes[self.which_eye(c.x_position, c.y_position)] += 1

    def update_heading(self):
        """This method updates the heading for the creature."""
        output: float = 0
        for i in range(evoflock.num_eyes):
            output += self.genotype[i + (self.predator_in_eye * evoflock.num_eyes)] * self.eyes[i]
        new_heading: float = self.heading + output
        self.heading = self.wrap_360(new_heading)

    def crossover(self, parent_a: int, parent_b: int):
        """This method is for performing crossover, where the genome of two parents are split and combined to create
        a new creature."""
        cutpoint: int = evoflock.random_int(evoflock.genotype_length)
        for i in range(evoflock.genotype_length - 1):
            if i < cutpoint:
                self.genotype[i] = evoflock.creatures[parent_a].genotype[i]
            else:
                self.genotype[i] = evoflock.creatures[parent_b].genotype[i]

    def mutate(self):
        """This method is for performing mutation, where random genomes are changed."""
        for i in range(evoflock.genotype_length):
            if random.random() > 0.9:
                mutation: float = random.random()
                if random.random() < 0.5:
                    mutation = -mutation
                self.genotype[i] = mutation


class Predator(Agent):
    def __init__(self, EvoFlock):
        super().__init__()
        self.speed = EvoFlock.predator_speed

    def update_predator(self):
        """This method finds the nearest creature to the predator and creates a new create via crossover
        and mutation if the creature gets caught."""
        self.nearest_creature: int = -1
        self.nearest_creature_distance: float = 999
        self.nearest_creature_heading: float = -1.0
        for creature in range(evoflock.num_creatures):
            dx = Decimal(str(evoflock.creatures[creature].x_position)) - Decimal(str(self.x_position))
            if dx < -0.5:
                dx += 1
            elif dx > 0.5:
                dx -= 1

            dy = Decimal(str(evoflock.creatures[creature].y_position)) - Decimal(str(self.y_position))
            if dy < -0.5:
                dy += 1
            elif dy > 0.5:
                dy -= 1

            d = math.sqrt((dx * dx) + (dy * dy))

            if d < self.nearest_creature_distance:
                self.nearest_creature = creature
                self.nearest_creature_distance = d
                self.nearest_creature_heading = super().wrap_360(math.degrees(math.atan2(-dy, dx)))

        if self.nearest_creature_distance < evoflock.creature_diameter:
            parent_a: int = random.randint(0, evoflock.num_creatures) - 1
            parent_b: int = random.randint(0, evoflock.num_creatures) - 1
            # Need to choose the creature that is not the one that just got caught
            while parent_a is self.nearest_creature:
                parent_a = random.randint(0, evoflock.num_creatures)

            while parent_b is self.nearest_creature and parent_b is not parent_a:
                parent_b = random.randint(0, evoflock.num_creatures)

            evoflock.creatures[self.nearest_creature].crossover(parent_a, parent_b)
            evoflock.creatures[self.nearest_creature].mutate()
            evoflock.reproductions += 1
            evoflock.creatures[self.nearest_creature].randomize_position_and_heading()

            self.randomize_position_and_heading()

        else:
            self.heading = self.nearest_creature_heading
            self.update_position()


def main_loop(evoflock):

    for c in evoflock.creatures:
        c.update_eyes()
        c.update_heading()
        c.update_position()
    evoflock.predator.update_predator()
    evoflock.counter += 1
    if evoflock.counter % 1 == 0:
        print("Counter = {counter}, Reproductions = {repos}".format(counter=evoflock.counter,
                                                                    repos=evoflock.reproductions))


if __name__ == '__main__':
    evoflock = EvoFlock()
    for creature in range(evoflock.num_creatures):
        evoflock.creatures.append(Creature(evoflock))
    while True:
        main_loop(evoflock)
