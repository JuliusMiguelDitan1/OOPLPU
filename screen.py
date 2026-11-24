
import pygame


class Screen:
    def __init__(self, width=900, height=560):
        pygame.init()

        pygame.display.set_caption(
            "Tiny Kingdom - OOP RPG"
        )

        self.surface = pygame.display.set_mode(
            (width, height)
        )

        self.width = width
        self.height = height

        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 34)

    def text(
        self,
        message,
        x,
        y,
        color=(240, 243, 250),
        font=None
    ):
        image = (font or self.font).render(
            str(message),
            True,
            color
        )

        self.surface.blit(image, (x, y))

    def draw(
        self,
        world,
        message,
        show_inventory=False,
        won=False,
        lost=False,
        dialogue=None
    ):
        self.surface.fill((24, 32, 45))

        # Header
        pygame.draw.rect(
            self.surface,
            (15, 21, 32),
            (0, 0, self.width, 58)
        )

        self.text(
            "TINY KINGDOM",
            20,
            15,
            (255, 220, 120),
            self.title_font
        )

        hero = world.hero

        self.text(
            f"HP: {hero.hp}/{hero.max_hp}   "
            f"Mana: {hero.mana}   "
            f"Gold: {hero.currency}",
            250,
            20
        )

        # Play field
        pygame.draw.rect(
            self.surface,
            (48, 76, 65),
            world.bounds,
            border_radius=12
        )

        pygame.draw.rect(
            self.surface,
            (105, 145, 116),
            world.bounds,
            3,
            border_radius=12
        )

        # Map grid
        for x in range(
            world.bounds.left + 20,
            world.bounds.right,
            40
        ):
            pygame.draw.line(
                self.surface,
                (53, 82, 70),
                (x, world.bounds.top),
                (x, world.bounds.bottom),
                1
            )

        for y in range(
            world.bounds.top + 20,
            world.bounds.bottom,
            40
        ):
            pygame.draw.line(
                self.surface,
                (53, 82, 70),
                (world.bounds.left, y),
                (world.bounds.right, y),
                1
            )

        # Ground items
        for drop in world.ground_items:
            pygame.draw.rect(
                self.surface,
                (235, 80, 115),
                drop["rect"],
                border_radius=5
            )

            pygame.draw.rect(
                self.surface,
                (255, 225, 235),
                drop["rect"],
                2,
                border_radius=5
            )
        #NPCs
        for npc in world.npcs:
            npc.draw(self.surface, self.small_font)

        # Enemies
        for enemy in world.enemies:
            if enemy.alive:
                enemy.draw(self.surface)

                self.text(
                    enemy.name,
                    enemy.x - 10,
                    enemy.y + enemy.size + 2,
                    (255, 235, 220),
                    self.small_font
                )

        # Hero
        hero.draw(self.surface)

        self.text(
            "YOU",
            hero.x - 2,
            hero.y + hero.size + 2,
            (220, 240, 255),
            self.small_font
        )

        # Controls
        pygame.draw.rect(
            self.surface,
            (15, 21, 32),
            (0, self.height - 50, self.width, 50)
        )

        self.text(
            "WASD Move | SPACE Attack | F Power Strike | "
            "E Collect | H Potion | I Inventory | ESC Quit | T talk to NPC",
            18,
            self.height - 35,
            (220, 230, 240),
            self.small_font
        )

        self.text(
            message,
            24,
            64,
            (255, 245, 160),
            self.small_font
        )

        # Inventory panel
        if show_inventory:
            panel = pygame.Rect(
                self.width - 260,
                75,
                235,
                130
            )

            pygame.draw.rect(
                self.surface,
                (20, 27, 40),
                panel,
                border_radius=8
            )

            pygame.draw.rect(
                self.surface,
                (130, 170, 220),
                panel,
                2,
                border_radius=8
            )

            self.text(
                "INVENTORY",
                panel.x + 14,
                panel.y + 12,
                (255, 220, 120)
            )

            self.text(
                f"Potions: {len(hero.inventory.items)}",
                panel.x + 14,
                panel.y + 45
            )

            self.text(
                "Press H to use a potion",
                panel.x + 14,
                panel.y + 75,
                font=self.small_font
            )

        if dialogue and dialogue.active:
            dialogue.draw(
                self.surface,
                self.font,
                self.small_font
            )

        # Victory or defeat
        if won or lost:
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 175))
            self.surface.blit(overlay, (0, 0))

            title = "VICTORY!" if won else "GAME OVER"

            self.text(
                title,
                self.width // 2 - 90,
                self.height // 2 - 35,
                (255, 220, 120),
                self.title_font
            )

            self.text(
                "Close the window to exit",
                self.width // 2 - 105,
                self.height // 2 + 10
            )

        pygame.display.flip()
