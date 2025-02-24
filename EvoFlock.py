import random
import math

class EvoFlock:
    """EvoFlock is a simulation of a predator-prey scenario where the prey are subject to an Evolutionary Algorithm.
    Each time a prey is caught, a new one is produced via crossover and mutation. Over time, the prey (creatures) will
    evolve to flock together away from the predator."""
    def __init__(self, bounded=True, num_creatures=50, selection_method='Rank', randomness_factor=0.1, tournament_size=3,
                 predator_type='simple', creature_type='simple'):
        self.reproductions: int = 0
        self.bounded = bounded
        self.timesteps = 0

        # Creature Variables
        self.creature_speed: float = 0.01
        self.predator_speed: float = 0.013
        self.creature_diameter: float = 0.015
        self.num_creatures: int = num_creatures

        self.num_eyes: int = 8

        self.selection_method = selection_method
        self.selection_randomness = randomness_factor
        self.selection_tournament_size = tournament_size
        self.predator_type = predator_type
        self.creature_type = creature_type

        self.closest_prey = -1
        self.creatures = []
        self.create_creatures()
        self.best_creature = 0
        self.predator_mutation_rate = 0.2
        self.predator = Predator(self, mode=predator_type, evolution_threshold=1000)

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
        [self.creatures.append(Creature(self, 'simple')) for _ in range(self.num_creatures)]

    def select_parents(self):
        """Selects two parents based on the specified method."""
        parent_a, parent_b = None, None
        method = self.selection_method
        if method == 'random':
            # Random selection
            # While parent_a is the caught creature or None select a new creature
            while (parent_a := self.creatures[random.randint(0, self.num_creatures - 1)]) is self.closest_prey or parent_a is None:
                pass
            # While parent_b is the caught creature, parent_a or None select a new creature
            while (parent_b := self.creatures[random.randint(0, self.num_creatures - 1)]) is self.closest_prey or parent_b is parent_a or parent_b is None:
                pass

        elif method == 'rank':
            randomness_factor = self.selection_randomness
            # Rank selection with optional randomness
            ranked_population = sorted(self.creatures, key=lambda x: x.lifespan, reverse=True)
            n = len(ranked_population)
            rank_sum = n * (n + 1) / 2
            selection_probabilities = [(n - i) / rank_sum for i in range(n)]

            def select_individual(randomness_factor):
                rand = random.random() * (1 - randomness_factor) + randomness_factor * random.random()
                cumulative_probability = 0.0
                for individual, probability in zip(ranked_population, selection_probabilities):
                    cumulative_probability += probability
                    if rand < cumulative_probability:
                        return individual

            while (parent_a := select_individual(randomness_factor)) is self.closest_prey:
                pass
            while (parent_b := select_individual(randomness_factor)) is parent_a or parent_b is self.closest_prey:
                pass

        elif method == 'tournament':
            tournament_size = self.selection_tournament_size
            # Tournament selection
            def select_individual():
                tournament = random.sample(self.creatures, tournament_size)
                return max(tournament, key=lambda x: x.lifespan)

            while (parent_a := select_individual()) is self.closest_prey:
                pass
            while (parent_b := select_individual()) is parent_a or parent_b is self.closest_prey:
                pass

        return parent_a, parent_b

    def create_new_creature(self):
        """When a creature is caught by the predator, a new creature must be made. The parents are selected,
        crossover and mutation is applied, then it is released into the world with a random position and heading."""
        parent_a, parent_b = self.select_parents()

        self.closest_prey.crossover(parent_a, parent_b)
        self.closest_prey.mutate()
        self.reproductions += 1
        self.closest_prey.randomize_position()
        self.closest_prey.randomize_heading()

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
        self.timesteps += 1

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

    def which_eye(self, x: float, y: float) -> int:
        """This method is used to determine which eye the creatures are seen in."""
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
        """This method is used update the number of creatures seen in each eye for this creature"""
        self.eyes = [0] * self.evoflock.num_eyes

        for c in self.evoflock.creatures:
            if c is not self:
                eye_index = self.which_eye(c.x_position, c.y_position)
                if eye_index != -1:
                    self.eyes[eye_index] += 1

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
    def __init__(self, evoflock, mode):
        super().__init__(evoflock)
        self.eyes = [0] * evoflock.num_eyes
        self.predator_in_eye: int = 0
        self.genotype_length: int = evoflock.num_eyes**2
        self.size = evoflock.creature_diameter
        if mode == 'simple':
            self.genotype = [0.0] * self.genotype_length
        else:
            self.genotype_length += 4  # 4 new attributes (speed, size, number of eyes, distance to predator) + eyes
            self.genotype = [random.uniform(-1, 1) for _ in range(self.genotype_length)]
        self.speed = evoflock.creature_speed
        self.lifespan = 0

        # for genome in range(len(self.genotype)):
        #     self.genotype[genome] = evoflock.random_float(2) - 1

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
        """This method updates what each creature sees in each eye. Need to account for Predator size."""
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
        main_parent = parent_a if self.evoflock.random_float(1) > 0.5 else parent_b
        cutpoint: int = self.evoflock.random_int(main_parent.genotype_length)
        for i in range(main_parent.genotype_length):
            if i < cutpoint:
                self.genotype[i] = parent_a.genotype[i]
            else:
                self.genotype[i] = parent_b.genotype[i]

    def mutate(self):
        """This method is for performing mutation, where random genomes are changed."""
        for i in range(self.genotype_length):
            if random.random() > 0.9:
                mutation: float = self.evoflock.random_float(1)
                if random.random() < 0.5:
                    mutation = -mutation
                self.genotype[i] = mutation


class Predator(Agent):
    def __init__(self, evoflock, mode='simple', evolution_threshold=1000):
        super().__init__(evoflock)
        self.mode = mode  # 'simple' or 'advanced'
        self.evolution_threshold = evolution_threshold
        self.creatures_caught = 0  # Track the number of creatures caught

        if self.mode == 'advanced':
            self.genotype_length = 3# + self.evoflock.num_eyes  # Speed, Size, Number of Eyes
            self.genotype = [random.uniform(-1, 1) for _ in range(self.genotype_length)]
            self.mutation_log = []  # Log of mutations and their performance
        self.speed = self.evoflock.predator_speed
        self.size = self.evoflock.creature_diameter
        self.num_eyes = self.evoflock.num_eyes
        self.eyes = [0] * self.evoflock.num_eyes

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
                self.evoflock.closest_prey = self.evoflock.creatures[creature]
                self.nearest_creature_distance = d
                self.nearest_creature_heading = self.wrap_360(math.degrees(math.atan2(-dy, dx)))

        if self.nearest_creature_distance < self.evoflock.creature_diameter:
            self.evoflock.create_new_creature()
            self.creatures_caught += 1

            if self.mode == 'advanced':
                # Update the mutation log with the number of creatures caught
                if self.mutation_log:
                    self.mutation_log[-1]['creatures_caught'] += 1
        else:
            if self.evoflock.timesteps % self.evolution_threshold == 0 and self.evoflock.timesteps > 0:
                self.check_for_crossover()
                self.mutate()
                self.creatures_caught = 0  # Reset the count
            self.heading = self.nearest_creature_heading
        self.update_position()

    def update_attributes(self):
        """Update predator attributes based on the genotype."""
        if self.mode == 'advanced':
            self.speed = self.map_genotype_to_range(self.genotype[0], self.evoflock.predator_speed-0.005, self.evoflock.predator_speed+0.005)
            self.size = self.map_genotype_to_range(self.genotype[1], self.evoflock.creature_diameter - 0.01, self.evoflock.creature_diameter + 0.01)  # Example size range
            self.num_eyes = int(self.map_genotype_to_range(self.genotype[2], 1, 12))  # Example eyes range
            ### The number of eyes aren't used in the same way as they are for creatures

    def map_genotype_to_range(self, value, min_val, max_val):
        """Map a genotype value from [-1, 1] to a specified range [min_val, max_val]."""
        return (value + 1) / 2 * (max_val - min_val) + min_val

    def mutate(self):
        """Perform mutation on the predator's genotype and log the mutation."""
        if self.mode == 'advanced':
            original_genotype = self.genotype.copy()

            for i in range(self.genotype_length):
                if random.random() < self.evoflock.predator_mutation_rate:
                    self.genotype[i] = random.uniform(-1, 1)
            self.update_attributes()
            self.mutation_log.append({
                'original': original_genotype,
                'mutated': self.genotype.copy(),
                'timestamp': self.evoflock.timesteps,
                'creatures_caught': 0
            })

    def select_parent_mutations(self):
        """Selects two parent mutations based on the specified method."""
        parent_a, parent_b = None, None
        method = self.evoflock.selection_method
        if method == 'random':
            # Random selection
            # While parent_a is the caught creature or None select a new creature
            while (parent_a := random.choice(self.mutation_log)):
                pass
            # While parent_b is the caught creature, parent_a or None select a new creature
            while (parent_b := random.choice(self.mutation_log)) is parent_a:
                pass

        elif method == 'rank':
            randomness_factor = self.evoflock.selection_randomness
            # Rank selection with optional randomness
            ranked_population = sorted(self.mutation_log, key=lambda x: x['creatures_caught'], reverse=True)
            n = len(ranked_population)
            rank_sum = n * (n + 1) / 2
            selection_probabilities = [(n - i) / rank_sum for i in range(n)]

            def select_individual(randomness):
                rand = random.random() * (1 - randomness) + randomness * random.random()
                cumulative_probability = 0.0
                for individual, probability in zip(ranked_population, selection_probabilities):
                    cumulative_probability += probability
                    if rand < cumulative_probability:
                        return individual

            while (parent_a := select_individual(randomness_factor)) is None:
                pass
            while (parent_b := select_individual(randomness_factor)) is parent_a or parent_b is None:
                pass

        elif method == 'tournament':
            tournament_size = self.evoflock.selection_tournament_size
            # Tournament selection
            def select_individual():
                tournament = random.sample(self.mutation_log, tournament_size)
                return max(tournament, key=lambda x: x.lifespan)

            while (parent_a := select_individual()):
                pass
            while (parent_b := select_individual()) is parent_a:
                pass

        return parent_a['mutated'], parent_b['mutated']

    def check_for_crossover(self):
        """Check if there are enough mutations to perform crossover."""
        if self.mode == 'advanced' and len(self.mutation_log) >= 5:
            # Sort mutations by performance (creatures caught)
            self.mutation_log.sort(key=lambda x: x['creatures_caught'], reverse=True)
            mutation_log_list_sorted = self.mutation_log
            print([x['creatures_caught'] for x in mutation_log_list_sorted])
            # Perform crossover between the top two mutations
            # parent_a = self.mutation_log[0]['mutated']
            # parent_b = self.mutation_log[1]['mutated']
            parent_a, parent_b = self.select_parent_mutations()
            cutpoint = random.randint(1, self.genotype_length - 1)
            self.genotype = parent_a[:cutpoint] + parent_b[cutpoint:]
            self.update_attributes()

            # Clear the mutation log
            # self.mutation_log = []

# class Predator(Agent):
#     def __init__(self, evoflock, mode='simple', evolution_threshold=5):
#         super().__init__(evoflock)
#         self.mode = mode  # 'simple' or 'advanced'
#         self.evolution_threshold = evolution_threshold
#         self.creatures_caught = 0  # Track the number of creatures caught
#
#
#         if self.mode == 'advanced':
#             self.genotype_length = 3  # Speed, Size, Number of Eyes
#             self.genotype = [random.uniform(-1, 1) for _ in range(self.genotype_length)]
#             self.mutation_log = []  # Log of mutations and their performance
#             self.update_attributes()
#         else:
#             self.speed = self.evoflock.predator_speed
#             self.size = self.evoflock.creature_diameter
#             self.num_eyes = self.evoflock.num_eyes
#             self.eyes = [0] * self.evoflock.num_eyes
#
#
#     def update_attributes(self):
#         """Update predator attributes based on the genotype."""
#         if self.mode == 'advanced':
#             self.speed = self.map_genotype_to_range(self.genotype[0], self.evoflock.predator_speed-0.03, self.evoflock.predator_speed+0.1)
#             self.size = self.map_genotype_to_range(self.genotype[1], self.evoflock.creature_diameter - 0.05, self.evoflock.creature_diameter + 0.05)  # Example size range
#             self.num_eyes = int(self.map_genotype_to_range(self.genotype[2], 1, 12))  # Example eyes range
#
#     def map_genotype_to_range(self, value, min_val, max_val):
#         """Map a genotype value from [-1, 1] to a specified range [min_val, max_val]."""
#         return (value + 1) / 2 * (max_val - min_val) + min_val
#
#     def calculate_creature_density(self, angle_step=45):
#         """Calculate the density of creatures in different directions."""
#         density = {}
#         for angle in range(0, 360, angle_step):
#             density[angle] = 0
#             for creature in self.evoflock.creatures:
#                 dx = creature.x_position - self.x_position
#                 dy = creature.y_position - self.y_position
#                 creature_angle = math.degrees(math.atan2(dy, dx)) - self.heading
#                 if -angle_step/2 <= creature_angle % 360 < angle_step/2:
#                     density[angle] += 1
#         return density
#
#     def select_direction_based_on_density(self, density):
#         """Select the direction with the highest creature density."""
#         max_density_angle = max(density, key=density.get)
#         return max_density_angle
#
#     def update_predator(self):
#         """This method finds the nearest creature to the predator and creates a new creature via crossover
#         and mutation if the creature gets caught."""
#         self.nearest_creature_distance: float = 999
#         self.nearest_creature_heading: float = -1.0
#         for creature in range(self.evoflock.num_creatures):
#             dx = float(self.evoflock.creatures[creature].x_position - self.x_position)
#             dy = float(self.evoflock.creatures[creature].y_position - self.y_position)
#
#             if not self.evoflock.bounded:
#                 if dx < -0.5:
#                     dx += 1
#                 elif dx > 0.5:
#                     dx -= 1
#
#                 if dy < -0.5:
#                     dy += 1
#                 elif dy > 0.5:
#                     dy -= 1
#
#             d = math.sqrt((dx * dx) + (dy * dy))
#
#             if d < self.nearest_creature_distance:
#                 self.evoflock.closest_prey = self.evoflock.creatures[creature]
#                 self.nearest_creature_distance = d
#                 self.nearest_creature_heading = self.wrap_360(math.degrees(math.atan2(-dy, dx)))
#
#         # Calculate creature density
#         density = self.calculate_creature_density()
#         max_density_angle = self.select_direction_based_on_density(density)
#
#         # Combine closest creature and density-based direction
#         weight_closest = 0.7  # Weight for the closest creature
#         weight_density = 0.3  # Weight for the density-based direction
#         combined_heading = (weight_closest * self.nearest_creature_heading +
#                             weight_density * max_density_angle) % 360
#
#         self.heading = combined_heading
#         self.update_position()
#
#         # Check if the predator caught a creature
#         if self.nearest_creature_distance < self.evoflock.creature_diameter:
#             self.creatures_caught += 1
#
#             if self.mode == 'advanced':
#                 # Update the mutation log with the number of creatures caught
#                 if self.mutation_log:
#                     self.mutation_log[-1]['creatures_caught'] += 1
#
#                 # Perform mutation if the threshold is met
#                 if self.creatures_caught >= self.evolution_threshold:
#                     self.mutate()
#                     self.creatures_caught = 0  # Reset the count
#
#                 # Reset the caught creature
#                 self.evoflock.creatures[closest_prey].randomize_position()
#                 self.evoflock.creatures[closest_prey].randomize_heading()
#                 self.evoflock.reproductions += 1
#
#         # Check for crossover opportunity in advanced mode
#         if self.mode == 'advanced':
#             self.check_for_crossover()
#
#     def mutate(self):
#         """Perform mutation on the predator's genotype and log the mutation."""
#         if self.mode == 'advanced':
#             original_genotype = self.genotype.copy()
#             for i in range(self.genotype_length):
#                 if random.random() < self.evoflock.predator_mutation_rate:
#                     self.genotype[i] = random.uniform(-1, 1)
#             self.update_attributes()
#             self.mutation_log.append({
#                 'original': original_genotype,
#                 'mutated': self.genotype.copy(),
#                 # 'timestamp': self.evoflock.counter,
#                 'creatures_caught': 0
#             })
#
#     def check_for_crossover(self):
#         """Check if there are enough mutations to perform crossover."""
#         if self.mode == 'advanced' and len(self.mutation_log) >= 2:
#             # Sort mutations by performance (creatures caught)
#             self.mutation_log.sort(key=lambda x: x['creatures_caught'], reverse=True)
#
#             # Perform crossover between the top two mutations
#             parent_a = self.mutation_log[0]['mutated']
#             parent_b = self.mutation_log[1]['mutated']
#             cutpoint = random.randint(1, self.genotype_length - 1)
#             self.genotype = parent_a[:cutpoint] + parent_b[cutpoint:]
#             self.update_attributes()
#
#             # Clear the mutation log
#             self.mutation_log = []