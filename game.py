
import pygame

from screen import Screen
from world import World
from hero import HERO_CLASSES
from dialogue import DialogueBox


class Game:
    MAIN_MENU = 'main_menu'
    SELECT = 'select'
    PLAYING = 'playing'
    HELP = 'help'
    LEVEL_DONE = 'level_done'
    GAME_OVER = 'game_over'
    COMPLETE = 'complete'

    def __init__(self):
        self.screen = Screen()
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = self.MAIN_MENU
        self.menu_choice = 0
        self.class_index = 0

        self.hero = None
        self.world = None

        self.dialogue = DialogueBox()
        self.current_npc = None

        self.message = 'Choose a hero to begin.'
        self.show_inventory = False

    def start_game(self):
        hero_class = HERO_CLASSES[self.class_index]

        self.hero = hero_class(
            70,
            self.screen.height // 2
        )

        self.world = World(
            self.screen.width,
            self.screen.height,
            self.hero
        )

        self.dialogue = DialogueBox()
        self.current_npc = None

        self.message = (
            f'{hero_class.CLASS_NAME} selected. '
            'Complete the tutorial first!'
        )

        self.show_inventory = False
        self.state = self.PLAYING

    def interact_npc(self):
        npc = self.world.nearest_npc()

        if not npc:
            self.message = 'No NPC nearby.'
            return

        quest = npc.quest

        if quest:
            if quest.status == 'completed':
                if quest.claim(self.hero.inventory):
                    self.message = (
                        f'Quest complete! '
                        f'Received {quest.reward_name}.'
                    )
                return

            if quest.status == 'claimed':
                self.message = (
                    'You already claimed this quest reward.'
                )
                return

            extra = []

            if quest.status == 'available':
                extra = [
                    f'Quest: {quest.title}.',
                    f'Defeat {quest.required_kills} enemies.',
                    f'Reward: {quest.reward_name}. '
                    'Finish talking to accept.'
                ]

            elif quest.status == 'active':
                extra = [
                    f'Quest: {quest.title}.',
                    f'Progress: '
                    f'{quest.kills}/{quest.required_kills} enemies.'
                ]

            self.current_npc = npc
            self.dialogue.start(npc, extra)

        else:
            self.current_npc = npc
            self.dialogue.start(npc)

    def finish_dialogue(self):
        npc = self.current_npc
        self.current_npc = None

        if (
            npc
            and npc.quest
            and npc.quest.status == 'available'
        ):
            npc.quest.accept()

            self.message = (
                f'Quest accepted: {npc.quest.title}!'
            )

        elif (
            npc
            and npc.quest
            and npc.quest.status == 'active'
        ):
            self.message = (
                f'Quest progress: '
                f'{npc.quest.kills}/'
                f'{npc.quest.required_kills}.'
            )

    def attack_target(self, use_skill=False):
        # Select the range for the current attack.
        attack_range = (
            self.hero.SKILL_RANGE
            if use_skill
            else self.hero.ATTACK_RANGE
        )

        # Search for an enemy inside this class's range.
        enemy = self.world.nearest_enemy(
            max_distance=attack_range
        )

        if not enemy:
            self.message = (
                f'No enemy within {attack_range} px.'
            )
            return

        distance = self.hero.distance_to(enemy)

        if distance > attack_range:
            self.message = (
                f'Enemy is out of range '
                f'({distance:.0f}/{attack_range} px).'
            )
            return

        was_alive = enemy.alive
        old_hp = enemy.hp

        if use_skill:
            self.message = self.hero.use_skill(
                enemy,
                pygame.time.get_ticks() / 1000
            )

        else:
            self.message = self.hero.attack(enemy)

        # Tutorial counts successful hits on the dummy.
        if (
            getattr(enemy, 'is_dummy', False)
            and enemy.hp < old_hp
        ):
            self.world.level.register_dummy_hit()

        # Count a defeated enemy for active NPC quests.
        elif was_alive and not enemy.alive:
            self.world.level.register_enemy_kill()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            # MAIN MENU
            if self.state == self.MAIN_MENU:
                if key in (
                    pygame.K_UP,
                    pygame.K_w
                ):
                    self.menu_choice = (
                        self.menu_choice - 1
                    ) % 3

                elif key in (
                    pygame.K_DOWN,
                    pygame.K_s
                ):
                    self.menu_choice = (
                        self.menu_choice + 1
                    ) % 3

                elif key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                ):
                    if self.menu_choice == 0:
                        self.state = self.SELECT

                    elif self.menu_choice == 1:
                        self.state = self.HELP

                    else:
                        self.running = False

                elif key == pygame.K_ESCAPE:
                    self.running = False

            # CHARACTER SELECTION
            elif self.state == self.SELECT:
                if key in (
                    pygame.K_LEFT,
                    pygame.K_a
                ):
                    self.class_index = (
                        self.class_index - 1
                    ) % len(HERO_CLASSES)

                elif key in (
                    pygame.K_RIGHT,
                    pygame.K_d
                ):
                    self.class_index = (
                        self.class_index + 1
                    ) % len(HERO_CLASSES)

                elif key == pygame.K_RETURN:
                    self.start_game()

                elif key == pygame.K_ESCAPE:
                    self.state = self.MAIN_MENU

            # HELP SCREEN
            elif self.state == self.HELP:
                if key in (
                    pygame.K_ESCAPE,
                    pygame.K_RETURN
                ):
                    self.state = self.MAIN_MENU

            # GAMEPLAY
            elif self.state == self.PLAYING:
                if key == pygame.K_ESCAPE:
                    if self.dialogue.active:
                        self.dialogue.close()
                        self.current_npc = None

                    else:
                        self.state = self.MAIN_MENU

                elif key == pygame.K_t:
                    if self.dialogue.active:
                        ended = self.dialogue.advance()

                        if ended:
                            self.finish_dialogue()

                    else:
                        self.interact_npc()

                elif self.dialogue.active:
                    continue

                elif key == pygame.K_SPACE:
                    self.attack_target(False)

                elif key == pygame.K_f:
                    self.attack_target(True)

                elif key == pygame.K_e:
                    self.message = (
                        self.world.collect_nearby()
                    )

                elif key == pygame.K_h:
                    used = self.hero.inventory.use_first(
                        self.hero
                    )

                    if used:
                        self.message = f'Used {used}.'

                    else:
                        self.message = (
                            'No usable item '
                            '(or stats are full).'
                        )

                elif key == pygame.K_i:
                    self.show_inventory = (
                        not self.show_inventory
                    )

            # LEVEL COMPLETION
            elif self.state in (
                self.LEVEL_DONE,
                self.COMPLETE
            ):
                if key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                ):
                    if self.state == self.COMPLETE:
                        self.state = self.MAIN_MENU

                    else:
                        next_index = (
                            self.world.level_index + 1
                        )

                        if next_index < len(
                            self.world.LEVELS
                        ):
                            self.world.load_level(
                                next_index
                            )

                            self.message = (
                                f'Level {next_index + 1} begins!'
                            )

                            self.state = self.PLAYING

                        else:
                            self.state = self.COMPLETE

                elif key == pygame.K_ESCAPE:
                    self.state = self.MAIN_MENU

            # GAME OVER
            elif self.state == self.GAME_OVER:
                if key == pygame.K_RETURN:
                    self.start_game()

                elif key == pygame.K_ESCAPE:
                    self.state = self.MAIN_MENU

    def update(self, elapsed):
        if (
            self.state != self.PLAYING
            or self.dialogue.active
        ):
            return

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        speed = 210 * elapsed

        if (
            keys[pygame.K_w]
            or keys[pygame.K_UP]
        ):
            dy -= speed

        if (
            keys[pygame.K_s]
            or keys[pygame.K_DOWN]
        ):
            dy += speed

        if (
            keys[pygame.K_a]
            or keys[pygame.K_LEFT]
        ):
            dx -= speed

        if (
            keys[pygame.K_d]
            or keys[pygame.K_RIGHT]
        ):
            dx += speed

        self.hero.move(
            dx,
            dy,
            self.world.bounds
        )

        messages = self.world.update_enemies(
            elapsed
        )

        if messages:
            self.message = messages[-1]

        if not self.hero.alive:
            self.state = self.GAME_OVER

        elif self.world.level.completed:
            self.state = self.LEVEL_DONE

            self.message = (
                'Tutorial complete!'
                if self.world.level.tutorial
                else 'Level cleared!'
            )

    def draw(self):
        if self.state == self.MAIN_MENU:
            self.screen.draw_menu(
                self.menu_choice
            )

        elif self.state == self.SELECT:
            self.screen.draw_select(
                self.class_index,
                HERO_CLASSES
            )

        elif self.state == self.HELP:
            self.screen.draw_help()

        elif self.state in (
            self.PLAYING,
            self.LEVEL_DONE,
            self.GAME_OVER
        ):
            self.screen.draw(
                self.world,
                self.message,
                self.show_inventory,
                won=self.state == self.LEVEL_DONE,
                lost=self.state == self.GAME_OVER,
                dialogue=self.dialogue
            )

        elif self.state == self.COMPLETE:
            self.screen.surface.fill(
                self.screen.BG
            )

            self.screen.text(
                'YOU CLEARED EVERY LEVEL!',
                self.screen.width // 2,
                190,
                self.screen.GOLD,
                self.screen.title_font,
                True
            )

            self.screen.text(
                'Press ENTER to return to the main menu',
                self.screen.width // 2,
                275,
                self.screen.WHITE,
                self.screen.font,
                True
            )

            pygame.display.flip()

    def run(self):
        while self.running:
            elapsed = min(
                self.clock.tick(60) / 1000,
                0.05
            )

            self.handle_events()
            self.update(elapsed)
            self.draw()

        pygame.quit()
