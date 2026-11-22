
from characters import Character


class Weapon:
    def __init__(self, name="Rusty Sword", bonus_damage=4):
        self.name = name
        self.bonus_damage = bonus_damage


class Skill:
    def __init__(
        self,
        name="Power Strike",
        bonus_damage=10,
        cooldown=2.0
    ):
        self.name = name
        self.bonus_damage = bonus_damage
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
            "Potion",
            "Restores 25 HP"
        )

    # Polymorphism: Potion has its own use behavior
    def use(self, hero):
        if hero.hp < hero.max_hp:
            hero.heal(25)
            return True

        return False


class Inventory:
    def __init__(self):
        self.items = []

    # Aggregation: Inventory stores Item objects
    def add(self, item):
        self.items.append(item)

    def use_first(self, hero):
        for index, item in enumerate(self.items):
            if item.use(hero):
                self.items.pop(index)
                return item.name

        return None


class Hero(Character):
    def __init__(self, x, y):
        super().__init__(
            "Hero",
            x,
            y,
            max_hp=100,
            damage=12,
            color=(65, 155, 245)
        )

        self.mana = 30
        self.currency = 0

        # Association: Hero uses a Weapon and Skill
        self.weapon = Weapon()
        self.skill = Skill()

        # Composition: Hero owns its Inventory
        self.inventory = Inventory()

        self.inventory.add(Potion())
        self.inventory.add(Potion())

    def attack(self, target):
        if target and target.alive:
            total_damage = (
                self.damage + self.weapon.bonus_damage
            )

            target.take_damage(total_damage)

            return f"You hit {target.name}!"

        return "That enemy is already defeated."

    def use_skill(self, target, now):
        if self.mana < 10:
            return "Not enough mana!"

        if not self.skill.ready(now):
            return "Power Strike is cooling down."

        self.mana -= 10
        self.skill.last_used = now

        total_damage = (
            self.damage
            + self.weapon.bonus_damage
            + self.skill.bonus_damage
        )

        target.take_damage(total_damage)

        return f"Power Strike hits {target.name}!"

    def move(self, dx, dy, bounds):
        self.x = max(
            bounds.left,
            min(bounds.right - self.size, self.x + dx)
        )

        self.y = max(
            bounds.top,
            min(bounds.bottom - self.size, self.y + dy)
        )
