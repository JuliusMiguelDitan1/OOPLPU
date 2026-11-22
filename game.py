
import pygame

from screen import Screen
from world import World


class Game:
    def __init__(self):
        self.screen = Screen()

        self.world = World(
            self.screen.width,
            self.screen.height
        )

        self.clock = pygame.time.Clock()

        self.message = (
            "Defeat the enemies. Find the red potions!"
        )

        self.show_inventory = False
        self.running = True
        self.won = False
        self.lost = False

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                hero = self.world.hero

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    enemy = self.world.nearest_enemy()

                    if enemy:
                        self.message = hero.attack(enemy)
                    else:
                        self.message = (
                            "Move closer to an enemy to attack."
                        )

                elif event.key == pygame.K_f:
                    enemy = self.world.nearest_enemy()

                    if enemy:
                        now = pygame.time.get_ticks() / 1000

                        self.message = hero.use_skill(
                            enemy,
                            now
                        )
                    else:
                        self.message = "No enemy in range."

                elif event.key == pygame.K_e:
                    self.message = (
                        self.world.collect_nearby()
                    )

                elif event.key == pygame.K_h:
                    used = hero.inventory.use_first(hero)

                    if used:
                        self.message = f"Used {used}."
                    else:
                        self.message = (
                            "No usable potion "
                            "(or HP is full)."
                        )

                elif event.key == pygame.K_i:
                    self.show_inventory = (
                        not self.show_inventory
                    )

    def update(self, elapsed):
        if self.won or self.lost:
            return

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        speed = 210 * elapsed

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += speed

        self.world.hero.move(
            dx,
            dy,
            self.world.bounds
        )

        messages = self.world.update_enemies(elapsed)

        if messages:
            self.message = messages[-1]

        self.lost = not self.world.hero.alive

        self.won = all(
            not enemy.alive
            for enemy in self.world.enemies
        )

    def run(self):
        while self.running:
            elapsed = min(
                self.clock.tick(60) / 1000,
                0.05
            )

            self.handle_events()
            self.update(elapsed)

            self.screen.draw(
                self.world,
                self.message,
                self.show_inventory,
                self.won,
                self.lost
            )

        pygame.quit()
