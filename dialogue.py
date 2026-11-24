import pygame


class NPC:
    def __init__(self, name, x, y, lines, color=(245, 195, 75), size=32):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.lines = list(lines)
        self.color = color
        self.size = size

    def distance_to_hero(self, hero):
        return (
            (self.x - hero.x) ** 2
            + (self.y - hero.y) ** 2
        ) ** 0.5

    def draw(self, surface, font):
        rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.size,
            self.size
        )

        pygame.draw.rect(
            surface,
            self.color,
            rect,
            border_radius=7
        )

        pygame.draw.rect(
            surface,
            (20, 24, 35),
            rect,
            2,
            border_radius=7
        )

        label = font.render(self.name, True, (255, 240, 175))
        surface.blit(label, (self.x - 6, self.y + self.size + 2))


class DialogueBox:
    def __init__(self):
        self.active = False
        self.speaker = ""
        self.lines = []
        self.index = 0

    def start(self, npc):
        if not npc.lines:
            return
        self.active = True
        self.speaker = npc.name
        self.lines = npc.lines
        self.index = 0

    def advance(self):
        if not self.active:
            return
        self.index += 1
        if self.index >= len(self.lines):
            self.close()

    def close(self):
        self.active = False
        self.speaker = ""
        self.lines = []
        self.index = 0

    @property
    def current_line(self):
        if self.active and 0 <= self.index < len(self.lines):
            return self.lines[self.index]
        return ""

    def draw(self, surface, font, small_font):
        if not self.active:
            return

        width, height = surface.get_size()
        box = pygame.Rect(40, height - 185, width - 80, 125)

        pygame.draw.rect(surface, (18, 24, 38), box, border_radius=10)
        pygame.draw.rect(surface, (230, 195, 105), box, 2, border_radius=10)

        speaker_surf = font.render(self.speaker, True, (255, 220, 120))
        surface.blit(speaker_surf, (box.x + 18, box.y + 12))

        line_surf = font.render(self.current_line, True, (240, 243, 250))
        surface.blit(line_surf, (box.x + 18, box.y + 46))

        prompt = (
            "Press T for next line (ESC to close)"
            if self.index + 1 < len(self.lines)
            else "Press T to finish"
        )
        prompt_surf = small_font.render(prompt, True, (185, 200, 220))
        surface.blit(prompt_surf, (box.x + 18, box.y + 92))