
import pygame

from enemy import Enemy, FinalBoss
from hero import Hero, Potion


class World:
    def __init__(self, width, height):
        self.bounds = pygame.Rect(
            24, 70, width - 48, height - 100
        )

        self.hero = Hero(70, height // 2)

        # Aggregation: World contains enemy objects
        self.enemies = [
            Enemy(
                "Slime",
                330,
                170,
                hp=28,
                damage=7,
                color=(80, 190, 110)
            ),

            Enemy(
                "Goblin",
                510,
                350,
                hp=42,
                damage=10,
                color=(220, 125, 55)
            ),

            FinalBoss(
                width - 130,
                height // 2 - 20
            )
        ]

        # Aggregation: World contains ground items
        self.ground_items = [
            {
                "item": Potion(),
                "rect": pygame.Rect(220, 380, 24, 24)
            },
            {
                "item": Potion(),
                "rect": pygame.Rect(620, 150, 24, 24)
            }
        ]

    def nearest_enemy(self, max_distance=75):
        candidates = [
            enemy
            for enemy in self.enemies
            if enemy.alive
            and self.hero.distance_to(enemy) <= max_distance
        ]

        return min(
            candidates,
            key=lambda enemy: self.hero.distance_to(enemy),
            default=None
        )

    def collect_nearby(self):
        hero_rect = pygame.Rect(
            int(self.hero.x),
            int(self.hero.y),
            self.hero.size,
            self.hero.size
        )

        for drop in self.ground_items[:]:
            if hero_rect.inflate(28, 28).colliderect(
                drop["rect"]
            ):
                item = drop["item"]

                self.hero.inventory.add(item)
                self.ground_items.remove(drop)

                return f"Collected {item.name}!"

        return "No item nearby."

    def update_enemies(self, elapsed):
        messages = []
        hero = self.hero

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            distance = enemy.distance_to(hero)

            if distance > 48:
                speed = (
                    55 if not isinstance(enemy, FinalBoss)
                    else 38
                )

                dx = hero.x - enemy.x
                dy = hero.y - enemy.y

                length = max(
                    1,
                    (dx * dx + dy * dy) ** 0.5
                )

                enemy.x += dx / length * speed * elapsed
                enemy.y += dy / length * speed * elapsed

            else:
                enemy._attack_timer = (
                    getattr(enemy, "_attack_timer", 0)
                    + elapsed
                )

                if enemy._attack_timer >= 1.0:
                    messages.append(enemy.attack(hero))
                    enemy._attack_timer = 0

        return messages
