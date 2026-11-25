from characters import Character


class Enemy(Character):
    def __init__(self, name, x, y, hp=35, damage=8, color=(215, 75, 80), level=1):
        super().__init__(name, x, y, hp, damage, color, size=32)
        self.level = level

    def attack(self, target):
        if self.alive and target.alive:
            target.take_damage(self.damage)
            return f'{self.name} attacks for {self.damage} damage!'
        return 'No attack.'


class FinalBoss(Enemy):
    def __init__(self, x, y, level=1):
        super().__init__('Final Boss', x, y, hp=100 + level * 15,
                         damage=13 + level * 2, color=(145, 65, 190), level=level)
        self.size = 46

    def attack(self, target):
        if self.alive and target.alive:
            amount = self.damage + 5
            target.take_damage(amount)
            return f'The Final Boss unleashes a heavy strike ({amount} damage)!'
        return 'No attack.'


class TrainingDummy(Enemy):
    """A harmless practice target that continuously regenerates health."""
    is_dummy = True



    def __init__(self, x, y):
        super().__init__('Training Dummy', x, y, hp=250, damage=0,
                         color=(190, 145, 85), level=0)
        self.regen_per_second = 18

    def attack(self, target):
        return 'The training dummy cannot attack.'

    def update_regen(self, elapsed):
        if self.alive:
            self._hp = min(self.max_hp, self._hp + self.regen_per_second * elapsed)
