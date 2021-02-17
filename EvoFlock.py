import random
import math
from decimal import Decimal


class EvoFlock:
    """EvoFlock is a simulation of a predator-prey scenario where the prey are subject to an Evolutionary Algorithm.
    Each time a prey is caught, a new one is produced via crossover and mutation."""
    def __init__(self):
        self.counter: int = 0
        self.reproductions: int = 0

        # Creature Variables
        self.creature_speed: float = 0.01
        self.predator_speed: float = 0.015
        self.creature_diameter: float = 0.015
        self.num_creatures: int = 50

        self.num_eyes: int = 8
        self.genotype_length: int = self.num_eyes**2

        self.creatures = []
        self.create_creatures()
        self.predator = Predator(self)

        self.closest_prey = -1

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

    def create_creatures(self):
        """Creature the population of prey"""
        for creature in range(self.num_creatures):
            self.creatures.append(Creature(self))

    def main_loop(self):
        """Main loop of the application, updates the eyes, heading and positions of each prey before updating the
        predator's"""
        [c.update_eyes() for c in self.creatures]
        [c.update_heading() for c in self.creatures]
        [c.update_position() for c in self.creatures]
        self.predator.update_predator()
        self.counter += 1
  #      if self.counter % 1 == 0:
            # print("Counter = {counter}, Reproductions = {repos} ".format(counter=self.counter,
            #                                                              repos=self.reproductions))


class Agent:
    """Class defining the base attributes of an Agent in the suimulation. Creature and Predator will inherit from
    this class."""

    def __init__(self):
        self.x_position: float
        self.y_position: float
        self.speed: float = 0
        self.heading: float = 0
        self.randomize_position_and_heading()

    def wrap_360(self, h: float):
        """If the agent exceeds 0 or 360 degrees, need to wrap the rotation."""
        divisible = h % 360
        if divisible < 0:
            divisible += 360
        elif divisible > 360:
            divisible -= 360
        return divisible

    def randomize_position_and_heading(self):
        """Randomises the position and heading of the Agent on Initialisation."""
        self.x_position: float = EvoFlock.random_float(1)
        self.y_position: float = EvoFlock.random_float(1)
        self.heading: float = self.wrap_360(EvoFlock.random_int(360))

    def update_position(self):
        """Updates the position of the Agent"""
        self.x_position += math.cos(math.radians(self.heading)) * self.speed

        if self.x_position < 0:
            self.x_position += 1
        elif self.x_position > 1:
            self.x_position -= 1

        self.y_position -= math.sin(math.radians(self.heading)) * self.speed
        if self.y_position < 0:
            self.y_position += 1
        elif self.y_position > 1:
            self.y_position -= 1


class Creature(Agent):
    """This class defines the predators or prey. They inherits from the Agent class."""
    def __init__(self, evoflock):
        super().__init__()
        self.eyes = [0] * evoflock.num_eyes
        self.predator_in_eye: int = 0
        self.genotype = [0.0] * evoflock.genotype_length
        self.speed = evoflock.creature_speed
        self.evoflock = evoflock
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
        return int(((dh * self.evoflock.num_eyes) / 360))

    def update_eyes(self):
        """This method updates what each creature sees in each eye."""
        self.predator_in_eye = self.which_eye(self.evoflock.predator.x_position,
                                              self.evoflock.predator.y_position)
        for eye in range(len(self.eyes)):
            self.eyes[eye] = 0

        for c in self.evoflock.creatures:
            if c is not self:
                self.eyes[self.which_eye(c.x_position, c.y_position)] += 1

    def update_heading(self):
        """This method updates the heading for the creature."""
        output: float = 0
        for i in range(self.evoflock.num_eyes):
            output += (self.genotype[i + (self.predator_in_eye * self.evoflock.num_eyes)] * self.eyes[i])
        new_heading: float = self.heading + output
        self.heading = self.wrap_360(new_heading)

    def crossover(self, parent_a: int, parent_b: int):
        """This method is for performing crossover, where the genome of two parents are split and combined to create
        a new creature."""
        cutpoint: int = self.evoflock.random_int(self.evoflock.genotype_length)
        if parent_a == self.evoflock.num_creatures:
            parent_a -= 1
        if parent_b == self.evoflock.num_creatures:
            parent_b -= 1
        for i in range(0, self.evoflock.genotype_length - 1):
            try:
                if i < cutpoint:
                    self.genotype[i] = self.evoflock.creatures[parent_a].genotype[i]
                else:
                    self.genotype[i] = self.evoflock.creatures[parent_b].genotype[i]
            except IndexError as e:
                print(e)

    def mutate(self):
        """This method is for performing mutation, where random genomes are changed."""
        for i in range(self.evoflock.genotype_length):
            if random.random() > 0.9:
                mutation: float = random.random()
                if random.random() < 0.5:
                    mutation = -mutation
                self.genotype[i] = mutation


class Predator(Agent):
    def __init__(self, EvoFlock):
        super().__init__()
        self.evoflock = EvoFlock
        self.speed = EvoFlock.predator_speed

    def update_predator(self):
        """This method finds the nearest creature to the predator and creates a new create via crossover
        and mutation if the creature gets caught."""
        self.nearest_creature_distance: float = 999
        self.nearest_creature_heading: float = -1.0
        for creature in range(self.evoflock.num_creatures):
            dx = Decimal(str(self.evoflock.creatures[creature].x_position)) - Decimal(str(self.x_position))
            if dx < -0.5:
                dx += 1
            elif dx > 0.5:
                dx -= 1

            dy = Decimal(str(self.evoflock.creatures[creature].y_position)) - Decimal(str(self.y_position))
            if dy < -0.5:
                dy += 1
            elif dy > 0.5:
                dy -= 1

            d = math.sqrt((dx * dx) + (dy * dy))

            if d < self.nearest_creature_distance:
                EvoFlock.closest_prey = creature
                self.nearest_creature_distance = d
                self.nearest_creature_heading = super().wrap_360(math.degrees(math.atan2(-dy, dx)))

        if self.nearest_creature_distance < self.evoflock.creature_diameter:
            parent_a: int = random.randint(0, self.evoflock.num_creatures - 1)
            parent_b: int = random.randint(0, self.evoflock.num_creatures - 1)
            # Need to choose the creature that is not the one that just got caught
            while parent_a is EvoFlock.closest_prey:
                parent_a = random.randint(0, self.evoflock.num_creatures)

            while parent_b is EvoFlock.closest_prey and parent_b is not parent_a:
                parent_b = random.randint(0, self.evoflock.num_creatures)

            self.evoflock.creatures[EvoFlock.closest_prey].crossover(parent_a, parent_b)
            self.evoflock.creatures[EvoFlock.closest_prey].mutate()
            self.evoflock.reproductions += 1
            self.evoflock.creatures[EvoFlock.closest_prey].randomize_position_and_heading()

            self.randomize_position_and_heading()

        else:
            self.heading = self.nearest_creature_heading
            self.update_position()
