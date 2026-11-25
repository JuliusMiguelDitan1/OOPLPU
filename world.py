import random
import pygame

from enemy import Enemy, FinalBoss, TrainingDummy
from hero import Potion, Item
from dialogue import NPC, Quest


class Elixir(Item):
    def __init__(self):
        super().__init__('Mana Elixir', 'Restores 25 Mana')

    def use(self, hero):
        if hero.mana < hero.BASE_MANA:
            hero.mana = min(hero.BASE_MANA, hero.mana + 25)
            return True
        return False


class Level:
    """A level owns its map content and tracks level/tutorial progression."""
    def __init__(self, number, name, width, height, hero, enemy_specs, tutorial=False):
        self.number = number
        self.name = name
        self.tutorial = tutorial
        self.bounds = pygame.Rect(24, 70, width - 48, height - 100)
        hero.x, hero.y = 70, height // 2
        self.hero = hero
        self.completed = False
        self.tutorial_hits = 0
        self.tutorial_hits_required = 5
        self.enemies = []

        for spec in enemy_specs:
            if spec.get('dummy'):
                self.enemies.append(TrainingDummy(width // 2, height // 2))
            elif spec.get('boss'):
                self.enemies.append(FinalBoss(width - 130, height // 2 - 20, number))
            else:
                self.enemies.append(Enemy(
                    spec['name'], spec['x'], spec['y'],
                    hp=spec['hp'] + max(0, number) * 5,
                    damage=spec['damage'] + max(0, number),
                    color=spec['color'], level=number
                ))

        # NPC locations are randomized on every level load.
        positions = self._random_npc_positions(2 if not tutorial else 1)
        self.npcs = []
        if tutorial:
            gx, gy = positions[0]
            self.npcs.append(NPC(
                'Guide', gx, gy,
                ['Welcome to the training grounds!',
                 'Move with WASD. Approach the dummy and attack it.',
                 'Hit the regenerating dummy five times to finish the tutorial.'],
                color=(245, 195, 75)
            ))
        else:
            nx, ny = positions[0]
            quest = Quest(
                'Monster Hunter', 2, Potion, 'Potion'
            )
            self.npcs.append(NPC(
                'Quest Giver', nx, ny,
                ['Adventurer, can you help us?', 'Defeat two enemies and return for a reward.'],
                color=(100, 210, 230), quest=quest
            ))
            vx, vy = positions[1]
            supply_quest = Quest(
                'Supply Request', 1, Elixir, 'Mana Elixir'
            )
            self.npcs.append(NPC(
                'Villager', vx, vy,
                ['The monsters are troubling our village.', 'Please defeat an enemy and I will give you an elixir.'],
                color=(245, 195, 75), quest=supply_quest
            ))

        self.ground_items = [
            {'item': Potion(), 'rect': pygame.Rect(220, 380, 24, 24)},
            {'item': Potion(), 'rect': pygame.Rect(620, 150, 24, 24)}
        ]
        self._attack_timers = {}

    def _random_npc_positions(self, count):
        candidates = [
            (150, 130), (240, 420), (430, 125), (570, 410),
            (690, 170), (730, 360), (350, 390), (520, 250)
        ]
        random.shuffle(candidates)
        return candidates[:count]

    def nearest_npc(self, max_distance=75):
        options = [n for n in self.npcs if n.distance_to_hero(self.hero) <= max_distance]
        return min(options, key=lambda n: n.distance_to_hero(self.hero), default=None)

    
    def nearest_enemy(self, max_distance=75):
        options = [
            enemy for enemy in self.enemies
            if (
                enemy.alive
                and self.hero.distance_to(enemy) <= max_distance
            )
        ]

        return min(
            options,
            key=lambda enemy: self.hero.distance_to(enemy),
            default=None
        )


    def collect_nearby(self):
        hero_rect = pygame.Rect(int(self.hero.x), int(self.hero.y), self.hero.size, self.hero.size)
        for drop in self.ground_items[:]:
            if hero_rect.inflate(28, 28).colliderect(drop['rect']):
                item = drop['item']
                self.hero.inventory.add(item)
                self.ground_items.remove(drop)
                return f'Collected {item.name}!'
        return 'No item nearby.'

    def register_dummy_hit(self):
        if self.tutorial:
            self.tutorial_hits += 1
            if self.tutorial_hits >= self.tutorial_hits_required:
                self.completed = True

    def register_enemy_kill(self):
        for npc in self.npcs:
            if npc.quest:
                npc.quest.record_kill()

    def update_enemies(self, elapsed):
        messages = []
        hero = self.hero
        killed = []

        for enemy in self.enemies:
            if getattr(enemy, 'is_dummy', False):
                enemy.update_regen(elapsed)
                continue
            if not enemy.alive:
                continue

            distance = enemy.distance_to(hero)
            if distance > 48:
                speed = 38 if isinstance(enemy, FinalBoss) else 55
                dx, dy = hero.x - enemy.x, hero.y - enemy.y
                length = max(1, (dx * dx + dy * dy) ** 0.5)
                enemy.x += dx / length * speed * elapsed
                enemy.y += dy / length * speed * elapsed
            else:
                self._attack_timers[enemy] = self._attack_timers.get(enemy, 0) + elapsed
                if self._attack_timers[enemy] >= 1:
                    messages.append(enemy.attack(hero))
                    self._attack_timers[enemy] = 0

        # Count each enemy's death once by tracking it in the game controller.
        if not self.tutorial and all(not e.alive for e in self.enemies):
            self.completed = True
        return messages


class World:
    LEVELS = [
        ('Tutorial: Training Grounds', [dict(dummy=True)], True),
        ('Village Outskirts', [
            dict(name='Slime', x=330, y=170, hp=28, damage=7, color=(80, 190, 110)),
            dict(name='Goblin', x=510, y=350, hp=42, damage=10, color=(220, 125, 55)),
            dict(boss=True)
        ], False),
        ('Whispering Forest', [
            dict(name='Forest Wraith', x=330, y=170, hp=40, damage=9, color=(90, 170, 160)),
            dict(name='Dark Wolf', x=510, y=350, hp=48, damage=11, color=(110, 115, 140)),
            dict(boss=True)
        ], False),
        ('Forgotten Dungeon', [
            dict(name='Skeleton', x=330, y=170, hp=50, damage=11, color=(195, 195, 175)),
            dict(name='Cursed Knight', x=510, y=350, hp=65, damage=13, color=(115, 125, 150)),
            dict(boss=True)
        ], False)
    ]

    def __init__(self, width, height, hero):
        self.width, self.height = width, height
        self.hero = hero
        self.level_index = 0
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index
        name, specs, tutorial = self.LEVELS[index]
        self.level = Level(index + 1, name, self.width, self.height, self.hero, specs, tutorial)

    @property
    def bounds(self): return self.level.bounds
    @property
    def enemies(self): return self.level.enemies
    @property
    def npcs(self): return self.level.npcs
    @property
    def ground_items(self): return self.level.ground_items

    def nearest_npc(self): return self.level.nearest_npc()
    
    def nearest_enemy(self, max_distance=75):
        return self.level.nearest_enemy(max_distance)

    def collect_nearby(self): return self.level.collect_nearby()
    def update_enemies(self, elapsed): return self.level.update_enemies(elapsed)
