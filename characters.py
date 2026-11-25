from abc import ABC, abstractmethod
import pygame

class Character(ABC):
    def __init__(self, name, x, y, max_hp, damage, color, size=34):
        self.name = name
        self.x, self.y = float(x), float(y)
        self.max_hp = int(max_hp)
        self._hp = int(max_hp)  # Encapsulation
        self.damage = int(damage)
        self.color = color
        self.size = size

    @property
    def hp(self):
        return self._hp

    @property
    def alive(self):
        return self._hp > 0

    def take_damage(self, amount):
        self._hp = max(0, self._hp - max(0, int(amount)))

    def heal(self, amount):
        self._hp = min(self.max_hp, self._hp + max(0, int(amount)))

    def distance_to(self, other):
        return ((self.x-other.x)**2 + (self.y-other.y)**2)**0.5

    def draw(self, surface):
        rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        pygame.draw.rect(surface, self.color, rect, border_radius=7)
        pygame.draw.rect(surface, (20, 24, 35), rect, 2, border_radius=7)
        bar = pygame.Rect(int(self.x), int(self.y)-9, self.size, 5)
        pygame.draw.rect(surface, (65, 30, 30), bar)
        if self.max_hp:
            fill = pygame.Rect(bar.x, bar.y, int(bar.width*self.hp/self.max_hp), bar.height)
            pygame.draw.rect(surface, (70, 210, 100), fill)

    @abstractmethod
    def attack(self, target):
        raise NotImplementedError
