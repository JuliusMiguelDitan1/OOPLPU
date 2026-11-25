import pygame

class Screen:
    BG=(24,32,45); PANEL=(15,21,32); GOLD=(255,220,120); WHITE=(240,243,250)
    def __init__(self,width=900,height=560):
        pygame.init(); pygame.display.set_caption('Tiny Kingdom - OOP RPG')
        self.surface=pygame.display.set_mode((width,height)); self.width=width; self.height=height
        self.font=pygame.font.Font(None,25); self.small_font=pygame.font.Font(None,20); self.title_font=pygame.font.Font(None,42)
    def text(self,msg,x,y,color=None,font=None,center=False):
        image=(font or self.font).render(str(msg),True,color or self.WHITE)
        if center: x-=image.get_width()//2
        self.surface.blit(image,(x,y))
    def centered_lines(self,lines,start_y,spacing=34,color=None,font=None):
        for i,line in enumerate(lines): self.text(line,self.width//2,start_y+i*spacing,color,font,True)
    def draw_menu(self,choice):
        self.surface.fill(self.BG)
        self.text('TINY KINGDOM',self.width//2,105,self.GOLD,self.title_font,True)
        self.centered_lines(['A CLASSIC OOP RPG ADVENTURE','Explore • Fight • Level Up'],180,34)
        options=['START GAME','HOW TO PLAY','EXIT']
        for i,opt in enumerate(options):
            prefix='> ' if i==choice else '  '
            self.text(prefix+opt,self.width//2,300+i*45,self.GOLD if i==choice else self.WHITE,self.font,True)
        self.text('UP/DOWN to choose • ENTER to confirm',self.width//2,475,(185,200,220),self.small_font,True)
        pygame.display.flip()
    def draw_select(self, index, classes):
        self.surface.fill(self.BG)
        self.text('CHOOSE YOUR HERO', self.width // 2, 38,
                  self.GOLD, self.title_font, True)

        # Five equal-width cards fit inside the screen with even margins.
        margin = 22
        gap = 12
        card_width = (self.width - margin * 2 - gap * (len(classes) - 1)) // len(classes)
        card_y = 112
        card_height = 278

        for i, cls in enumerate(classes):
            card_x = margin + i * (card_width + gap)
            card = pygame.Rect(card_x, card_y, card_width, card_height)
            selected = i == index

            pygame.draw.rect(self.surface, (35, 45, 63), card, border_radius=12)
            pygame.draw.rect(
                self.surface,
                self.GOLD if selected else (90, 105, 125),
                card,
                3 if selected else 1,
                border_radius=12
            )

            # All content is centered relative to the same card rectangle.
            center_x = card.centerx
            icon_size = 46
            icon = pygame.Rect(center_x - icon_size // 2, card_y + 24,
                              icon_size, icon_size)
            pygame.draw.rect(self.surface, cls.COLOR, icon, border_radius=10)

            self.text(cls.CLASS_NAME, center_x, card_y + 88,
                     self.GOLD if selected else self.WHITE, self.font, True)
            self.text(f'HP  {cls.BASE_HP}', center_x, card_y + 132,
                     self.WHITE, self.small_font, True)
            self.text(f'Mana  {cls.BASE_MANA}', center_x, card_y + 164,
                     self.WHITE, self.small_font, True)
            self.text(f'Damage  {cls.BASE_DAMAGE}', center_x, card_y + 196,
                     self.WHITE, self.small_font, True)

            skill_text = cls.SKILL_NAME
            skill_font = self.small_font
            skill_surface = skill_font.render(skill_text, True, (185, 200, 220))
            # Keep long skills inside the card by scaling the font down as needed.
            if skill_surface.get_width() > card_width - 12:
                skill_font = pygame.font.Font(None, 17)
            self.text(skill_text, center_x, card_y + 238,
                      (185, 200, 220), skill_font, True)

        self.text('LEFT / RIGHT: Choose   •   ENTER: Select   •   ESC: Back',
                  self.width // 2, 430, (185, 200, 220), self.small_font, True)
        pygame.display.flip()

    def draw(self,world,message,show_inventory=False,won=False,lost=False,dialogue=None):
        self.surface.fill(self.BG); level=world.level; hero=world.hero
        pygame.draw.rect(self.surface,self.PANEL,(0,0,self.width,58))
        self.text(f'LEVEL {level.number}: {level.name}',18,15,self.GOLD,self.font)
        self.text(f'{hero.name}  HP {hero.hp}/{hero.max_hp}  Mana {hero.mana}  Gold {hero.currency}',370,20,self.WHITE,self.small_font)
        pygame.draw.rect(self.surface,(48,76,65),world.bounds,border_radius=12)
        pygame.draw.rect(self.surface,(105,145,116),world.bounds,3,border_radius=12)
        for x in range(world.bounds.left+20,world.bounds.right,40): pygame.draw.line(self.surface,(53,82,70),(x,world.bounds.top),(x,world.bounds.bottom),1)
        for y in range(world.bounds.top+20,world.bounds.bottom,40): pygame.draw.line(self.surface,(53,82,70),(world.bounds.left,y),(world.bounds.right,y),1)
        for drop in world.ground_items:
            pygame.draw.rect(self.surface,(235,80,115),drop['rect'],border_radius=5)
            pygame.draw.rect(self.surface,(255,225,235),drop['rect'],2,border_radius=5)
        for npc in world.npcs: npc.draw(self.surface,self.small_font)
        for enemy in world.enemies:
            if enemy.alive:
                enemy.draw(self.surface); self.text(enemy.name,enemy.x-10,enemy.y+enemy.size+2,(255,235,220),self.small_font)
        hero.draw(self.surface); self.text(hero.name,hero.x-2,hero.y+hero.size+2,(220,240,255),self.small_font)
        pygame.draw.rect(self.surface,self.PANEL,(0,self.height-50,self.width,50))
        self.text('WASD Move | SPACE Attack | F Class Skill | E Collect | H Potion | I Inventory | T Talk | ESC Menu',12,self.height-34,(220,230,240),self.small_font)
        self.text(message,24,64,(255,245,160),self.small_font)
        if level.tutorial:
            self.text(f'Tutorial: hit the dummy {level.tutorial_hits}/{level.tutorial_hits_required} times', 24, 86, self.GOLD, self.small_font)
        else:
            active_quests = [n.quest for n in world.npcs if n.quest and n.quest.status in ('active', 'completed')]
            if active_quests:
                q = active_quests[0]
                self.text(f'Quest: {q.title} ({q.kills}/{q.required_kills}) - Reward: {q.reward_name}', 24, 86, self.GOLD, self.small_font)
        if show_inventory:
            panel=pygame.Rect(self.width-260,75,235,130); pygame.draw.rect(self.surface,(20,27,40),panel,border_radius=8); pygame.draw.rect(self.surface,(130,170,220),panel,2,border_radius=8)
            self.text('INVENTORY',panel.x+14,panel.y+12,self.GOLD)
            self.text(f'Items: {len(hero.inventory.items)}',panel.x+14,panel.y+45)
            self.text('Press H to use a potion',panel.x+14,panel.y+75,font=self.small_font)
        if dialogue and dialogue.active: dialogue.draw(self.surface,self.font,self.small_font)
        if won or lost:
            overlay=pygame.Surface((self.width,self.height),pygame.SRCALPHA); overlay.fill((0,0,0,175)); self.surface.blit(overlay,(0,0))
            self.text('VICTORY!' if won else 'GAME OVER',self.width//2,self.height//2-35,self.GOLD,self.title_font,True)
            self.text('ENTER to continue' if won else 'ENTER to retry • ESC to menu',self.width//2,self.height//2+20,self.WHITE,self.font,True)
        pygame.display.flip()
    def draw_help(self):
        self.surface.fill(self.BG); self.text('HOW TO PLAY',self.width//2,100,self.GOLD,self.title_font,True)
        self.centered_lines(['Move with WASD or arrow keys.','SPACE: basic attack (near an enemy)','F: use your selected class skill','E: collect items • H: use potion • T: talk','Defeat all enemies to clear the level.','Press ESC to return.'],200,38)
        pygame.display.flip()
