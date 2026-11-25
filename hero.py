
from characters import Character


class Weapon:
    def __init__(self, name='Adventurer Weapon', bonus_damage=4):
        self.name = name
        self.bonus_damage = bonus_damage


class Skill:
    def __init__(
        self,
        name='Power Strike',
        bonus_damage=10,
        mana_cost=10,
        cooldown=2.0
    ):
        self.name = name
        self.bonus_damage = bonus_damage
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.last_used = -999.0

    def ready(self, now):
        return now - self.last_used >= self.cooldown


class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def use(self, hero):
        return False


class Potion(Item):
    def __init__(self):
        super().__init__(
            'Potion',
            'Restores 25 HP'
        )

    def use(self, hero):
        if hero.hp < hero.max_hp:
            hero.heal(25)
            return True

        return False


class Inventory:
    def __init__(self):
        self.items = []

    def add(self, item):
        # Aggregation: inventory stores independently-created items.
        self.items.append(item)

    def use_first(self, hero):
        for index, item in enumerate(self.items):
            if item.use(hero):
                self.items.pop(index)
                return item.name

        return None


class Hero(Character):
    CLASS_NAME = 'Adventurer'

    BASE_HP = 100
    BASE_MANA = 50
    BASE_DAMAGE = 12

    COLOR = (65, 155, 245)

    SKILL_NAME = 'Power Strike'
    SKILL_DAMAGE = 10
    SKILL_COST = 10

    # Default ranges, overridden by each playable class.
    ATTACK_RANGE = 60
    SKILL_RANGE = 80

    def __init__(self, x, y):
        super().__init__(
            self.CLASS_NAME,
            x,
            y,
            self.BASE_HP,
            self.BASE_DAMAGE,
            self.COLOR
        )

        self.mana = self.BASE_MANA
        self.currency = 0
        self.level = 1

        self.weapon = Weapon()

        self.skill = Skill(
            self.SKILL_NAME,
            self.SKILL_DAMAGE,
            self.SKILL_COST
        )

        # Composition: the hero owns their inventory.
        self.inventory = Inventory()

        self.inventory.add(Potion())
        self.inventory.add(Potion())

    def attack(self, target):
        if target and target.alive:
            damage = (
                self.damage
                + self.weapon.bonus_damage
            )

            target.take_damage(damage)

            return (
                f'{self.name} hits {target.name} '
                f'for {damage}!'
            )

        return 'That enemy is already defeated.'

    def use_skill(self, target, now):
        if not target or not target.alive:
            return 'No living target.'

        if self.mana < self.skill.mana_cost:
            return 'Not enough mana!'

        if not self.skill.ready(now):
            return f'{self.skill.name} is cooling down.'

        self.mana -= self.skill.mana_cost
        self.skill.last_used = now

        damage = (
            self.damage
            + self.weapon.bonus_damage
            + self.skill.bonus_damage
        )

        target.take_damage(damage)

        # Polymorphism: each class has its own skill effect.
        self.apply_skill_effect(target)

        return (
            f'{self.skill.name} hits {target.name} '
            f'for {damage}!'
        )

    def apply_skill_effect(self, target):
        """Overridden by subclasses."""
        return None

    def move(self, dx, dy, bounds):
        self.x = max(
            bounds.left,
            min(
                bounds.right - self.size,
                self.x + dx
            )
        )

        self.y = max(
            bounds.top,
            min(
                bounds.bottom - self.size,
                self.y + dy
            )
        )


class Mage(Hero):
    CLASS_NAME = 'Mage'

    BASE_HP = 80
    BASE_MANA = 100
    BASE_DAMAGE = 10

    COLOR = (120, 105, 235)

    SKILL_NAME = 'Fireball'
    SKILL_DAMAGE = 28
    SKILL_COST = 20

    ATTACK_RANGE = 180
    SKILL_RANGE = 220

    def apply_skill_effect(self, target):
        self.mana = min(
            self.BASE_MANA,
            self.mana + 5
        )


class Warrior(Hero):
    CLASS_NAME = 'Warrior'

    BASE_HP = 120
    BASE_MANA = 40
    BASE_DAMAGE = 16

    COLOR = (205, 85, 75)

    SKILL_NAME = 'Heavy Strike'
    SKILL_DAMAGE = 22
    SKILL_COST = 12

    ATTACK_RANGE = 55
    SKILL_RANGE = 65

    def apply_skill_effect(self, target):
        self.heal(5)


class Ranger(Hero):
    CLASS_NAME = 'Ranger'

    BASE_HP = 90
    BASE_MANA = 70
    BASE_DAMAGE = 13

    COLOR = (75, 175, 105)

    SKILL_NAME = 'Piercing Shot'
    SKILL_DAMAGE = 20
    SKILL_COST = 14

    ATTACK_RANGE = 200
    SKILL_RANGE = 250

    def apply_skill_effect(self, target):
        self.currency += 2


class Knight(Hero):
    CLASS_NAME = 'Knight'

    BASE_HP = 150
    BASE_MANA = 50
    BASE_DAMAGE = 11

    COLOR = (145, 165, 190)

    SKILL_NAME = 'Shield Bash'
    SKILL_DAMAGE = 16
    SKILL_COST = 12

    ATTACK_RANGE = 60
    SKILL_RANGE = 75

    def apply_skill_effect(self, target):
        target.take_damage(4)


class Paladin(Hero):
    CLASS_NAME = 'Paladin'

    BASE_HP = 110
    BASE_MANA = 90
    BASE_DAMAGE = 12

    COLOR = (225, 190, 75)

    SKILL_NAME = 'Holy Light'
    SKILL_DAMAGE = 20
    SKILL_COST = 16

    ATTACK_RANGE = 75
    SKILL_RANGE = 110

    def apply_skill_effect(self, target):
        self.heal(15)


HERO_CLASSES = [
    Mage,
    Warrior,
    Ranger,
    Knight,
    Paladin
]
