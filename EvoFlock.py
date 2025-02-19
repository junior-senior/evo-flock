import random
import math

class EvoFlock:
    """EvoFlock is a simulation of a predator-prey scenario where the prey are subject to an Evolutionary Algorithm.
    Each time a prey is caught, a new one is produced via crossover and mutation."""
    def __init__(self, bounded=True, num_creatures=50, selection_method='Rank', randomness_factor=0.1, tournament_size=3,
                 predator_type='simple', creature_type='simple'):
        self.counter: int = 0
        self.reproductions: int = 0
        self.bounded = bounded

        # Creature Variables
        self.creature_speed: float = 0.01
        self.predator_speed: float = 0.013
        self.creature_diameter: float = 0.015
        self.num_creatures: int = num_creatures

        self.num_eyes: int = 8
        self.genotype_length: int = self.num_eyes**2

        self.selection_method = selection_method
        self.selection_randomness = randomness_factor
        self.selection_tournament_size = tournament_size
        self.predator_type = predator_type
        self.creature_type = creature_type

        self.closest_prey = -1
        self.creatures = []
        self.create_creatures()
        self.best_creature = 0
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
        return math.cos(math.radians(h))

    @staticmethod
    def sin_degrees(h: float):
        """Gets the sin of an angle in degrees."""
        return math.sin(math.radians(h))

    def create_creatures(self):
        """Creates the population of prey"""
        for _ in range(self.num_creatures):
            self.creatures.append(Creature(self))

    def select_parents(self):
        """Selects two parents based on the specified method."""
        parent_a, parent_b = None, None
        method = self.selection_method
        if method == 'random':
            # Random selection
            while parent_a is self.closest_prey or parent_a is None:
                parent_a = random.randint(0, self.num_creatures - 1)

            while parent_b is self.closest_prey or parent_b is parent_a or parent_b is None:
                parent_b = random.randint(0, self.num_creatures - 1)

        elif method == 'rank':
            randomness_factor = self.selection_randomness
            # Rank selection with optional randomness
            ranked_population = sorted(self.creatures, key=lambda x: x.lifespan, reverse=True)
            n = len(ranked_population)
            rank_sum = n * (n + 1) / 2
            selection_probabilities = [(n - i) / rank_sum for i in range(n)]

            def select_individual():
                rand = random.random() * (1 - randomness_factor) + randomness_factor * random.random()
                cumulative_probability = 0.0
                for individual, probability in zip(ranked_population, selection_probabilities):
                    cumulative_probability += probability
                    if rand < cumulative_probability:
                        return individual

            parent_a = select_individual()
            while (parent_b := select_individual()) is parent_a or parent_b is self.closest_prey:
                pass

        elif method == 'tournament':
            tournament_size = self.selection_tournament_size
            # Tournament selection
            def select_individual():
                tournament = random.sample(self.creatures, tournament_size)
                return max(tournament, key=lambda x: x.lifespan)

            parent_a = select_individual()
            while (parent_b := select_individual()) is parent_a or parent_b is self.closest_prey:
                pass

        return parent_a, parent_b

    def create_new_creature(self):
        parent_a, parent_b = self.select_parents()

        self.creatures[self.closest_prey].crossover(parent_a, parent_b)
        self.creatures[self.closest_prey].mutate()
        self.reproductions += 1
        self.creatures[self.closest_prey].randomize_position()
        self.creatures[self.closest_prey].randomize_heading()

    def main_loop(self):
        """Main loop of the application, updates the eyes, heading and positions of each prey before updating the
        predator's"""
        [c.update_eyes() for c in self.creatures]
        [c.update_heading() for c in self.creatures]
        [c.update_position() for c in self.creatures]
        [c.resolve_collisions() for c in self.creatures]
        [c.update_lifespan() for c in self.creatures]
        self.best_creature = max(self.creatures, key=lambda creature: creature.lifespan).lifespan
        self.predator.update_predator()

class Agent:
    """Class defining the base attributes of an Agent in the simulation. Creature and Predator will inherit from
    this class."""

    def __init__(self, evoflock):
        self.evoflock = evoflock
        self.x_position: float = evoflock.random_float(1)
        self.y_position: float = evoflock.random_float(1)
        self.speed: float = 0
        self.heading: float = evoflock.random_int(360)

    def wrap_360(self, h: float):
        """If the agent exceeds 0 or 360 degrees, need to wrap the rotation."""
        return h % 360

    def randomize_position(self):
        """Randomises the position of the Agent."""
        self.x_position = self.evoflock.random_float(1)
        self.y_position = self.evoflock.random_float(1)

    def randomize_heading(self):
        """Randomises the heading of the Agent."""
        self.heading = self.wrap_360(self.evoflock.random_int(360))

    def update_position(self):
        """Updates the position of the Agent"""
        delta_x = self.evoflock.cos_degrees(self.heading) * self.speed
        delta_y = -self.evoflock.sin_degrees(self.heading) * self.speed

        self.x_position += delta_x
        self.y_position += delta_y

        if self.evoflock.bounded:
            # Check for boundary collision and adjust heading
            if self.x_position < 0:
                self.x_position = 0
                self.heading = random.uniform(0, 180)  # Turn to a random direction facing right
            elif self.x_position > 1:
                self.x_position = 1
                self.heading = random.uniform(180, 360)  # Turn to a random direction facing left

            if self.y_position < 0:
                self.y_position = 0
                self.heading = random.uniform(270, 90)  # Turn to a random direction facing up
            elif self.y_position > 1:
                self.y_position = 1
                self.heading = random.uniform(90, 270)  # Turn to a random direction facing down
        else:
            # Wrap around the environment
            if self.x_position < 0:
                self.x_position += 1
            elif self.x_position > 1:
                self.x_position -= 1

            if self.y_position < 0:
                self.y_position += 1
            elif self.y_position > 1:
                self.y_position -= 1

class Creature(Agent):
    """This class defines the predators or prey. They inherit from the Agent class."""
    def __init__(self, evoflock):
        super().__init__(evoflock)
        self.eyes = [0] * evoflock.num_eyes
        self.predator_in_eye: int = 0
        self.genotype = [0.0] * evoflock.genotype_length
        self.speed = evoflock.creature_speed
        self.lifespan = 0
        for genome in range(len(self.genotype)):
            self.genotype[genome] = evoflock.random_float(2) - 1

    def which_eye(self, x: float, y: float) -> int:
        """This method is used to determine which eye the predator is seen in for this creature."""
        dx: float = x - self.x_position
        dy: float = y - self.y_position

        if not self.evoflock.bounded:
            if dx < -0.5:
                dx += 1
            elif dx > 0.5:
                dx -= 1

            if dy < -0.5:
                dy += 1
            elif dy > 0.5:
                dy -= 1

        angle = math.degrees(math.atan2(-dy, dx)) - self.heading
        dh: float = self.wrap_360(angle)
        return int(((dh * self.evoflock.num_eyes) / 360))

    def update_eyes(self):
        """This method updates what each creature sees in each eye."""
        self.predator_in_eye = self.which_eye(self.evoflock.predator.x_position,
                                              self.evoflock.predator.y_position)
        self.eyes = [0] * self.evoflock.num_eyes

        for c in self.evoflock.creatures:
            if c is not self:
                eye_index = self.which_eye(c.x_position, c.y_position)
                if eye_index != -1:
                    self.eyes[eye_index] += 1

    def update_lifespan(self):
        self.lifespan += 1

    def resolve_collisions(self):
        """Adjusts the position of the creature to resolve collisions with other creatures"""
        for other in self.evoflock.creatures:
            if other is not self:
                dx = self.x_position - other.x_position
                dy = self.y_position - other.y_position
                distance = math.sqrt(dx * dx + dy * dy)

                # Check if the creatures are overlapping
                if distance < self.evoflock.creature_diameter:
                    if distance == 0:
                        # If distance is zero, add a small random perturbation
                        self.x_position += random.uniform(-0.01, 0.01)
                        self.y_position += random.uniform(-0.01, 0.01)
                    else:
                        # Adjust position to resolve overlap
                        overlap = self.evoflock.creature_diameter - distance
                        self.x_position += overlap * (dx / distance)
                        self.y_position += overlap * (dy / distance)

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
        for i in range(self.evoflock.genotype_length):
            if i < cutpoint:
                self.genotype[i] = parent_a.genotype[i]
            else:
                self.genotype[i] = parent_b.genotype[i]

    def mutate(self):
        """This method is for performing mutation, where random genomes are changed."""
        for i in range(self.evoflock.genotype_length):
            if random.random() > 0.9:
                mutation: float = random.random()
                if random.random() < 0.5:
                    mutation = -mutation
                self.genotype[i] = mutation

class Predator(Agent):
    def __init__(self, evoflock):
        super().__init__(evoflock)
        self.speed = evoflock.predator_speed
        self.predator_type = evoflock.predator_type
        self.eyes = [0] * evoflock.num_eyes

    def which_eye(self, x: float, y: float) -> int:
        """This method is used to determine which eye the predator is seen in for this creature."""
        dx: float = x - self.x_position
        dy: float = y - self.y_position

        if not self.evoflock.bounded:
            if dx < -0.5:
                dx += 1
            elif dx > 0.5:
                dx -= 1

            if dy < -0.5:
                dy += 1
            elif dy > 0.5:
                dy -= 1

        angle = math.degrees(math.atan2(-dy, dx)) - self.heading
        dh: float = self.wrap_360(angle)
        return int(((dh * self.evoflock.num_eyes) / 360))

    def update_eyes(self):

        self.eyes = [0] * self.evoflock.num_eyes

        for c in self.evoflock.creatures:
            if c is not self:
                eye_index = self.which_eye(c.x_position, c.y_position)
                if eye_index != -1:
                    self.eyes[eye_index] += 1


    def update_predator(self):
        """This method finds the nearest creature to the predator and creates a new creature via crossover
        and mutation if the creature gets caught."""
        self.nearest_creature_distance: float = 999
        self.nearest_creature_heading: float = -1.0
        for creature in range(self.evoflock.num_creatures):
            dx = float(self.evoflock.creatures[creature].x_position - self.x_position)
            dy = float(self.evoflock.creatures[creature].y_position - self.y_position)

            if not self.evoflock.bounded:
                if dx < -0.5:
                    dx += 1
                elif dx > 0.5:
                    dx -= 1

                if dy < -0.5:
                    dy += 1
                elif dy > 0.5:
                    dy -= 1

            d = math.sqrt((dx * dx) + (dy * dy))

            if d < self.nearest_creature_distance:
                self.evoflock.closest_prey = creature
                self.nearest_creature_distance = d
                self.nearest_creature_heading = self.wrap_360(math.degrees(math.atan2(-dy, dx)))

        if self.nearest_creature_distance < self.evoflock.creature_diameter:
            self.evoflock.create_new_creature()
        else:
            self.heading = self.nearest_creature_heading
            self.update_position()
