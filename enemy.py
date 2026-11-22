
from characters import Character


class Enemy(Character):
    def __init__(
        self,
        name,
        x,
        y,
        hp=35,
        damage=8,
        color=(215, 75, 80)
    ):
        super().__init__(
            name,
            x,
            y,
            hp,
            damage,
            color,
            size=32
        )

    def attack(self, target):
        if self.alive and target.alive:
            target.take_damage(self.damage)

            return (
                f"{self.name} attacks for "
                f"{self.damage} damage!"
            )

        return "No attack."


class FinalBoss(Enemy):
    def __init__(self, x, y):
        super().__init__(
            "Final Boss",
            x,
            y,
            hp=110,
            damage=15,
            color=(145, 65, 190)
        )

        self.size = 46

    # Polymorphism: different attack behavior
    def attack(self, target):
        if self.alive and target.alive:
            boss_damage = self.damage + 5

            target.take_damage(boss_damage)

            return (
                "The Final Boss unleashes a heavy strike "
                f"({boss_damage} damage)!"
            )

        return "No attack."
