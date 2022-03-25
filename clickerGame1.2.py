import pygame
import random
from pygame.locals import (K_w, K_a, K_s, K_d, MOUSEBUTTONUP, K_ESCAPE, KEYDOWN, QUIT, )

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

SPRITE_HEIGHT = 200

factor = 1
score = 30
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BONUS_CHANCE = .1


def get_image_names(themes):
    _background_names, _player_names, _resource_names, _drop_names = [], [], [], []
    for theme in themes:
        _background_names.append(theme + '_background')
        _player_names.append(theme + '_player')
        _resource_names.append(theme + '_resource')
        _drop_names.append(theme + '_drop')

    return _background_names, _player_names, _resource_names, _drop_names


background_names, player_names, resource_names, drop_names = get_image_names(['lionking', 'synthwave', 'ruegenwalder'])
music_names = ['sound/LionKing.ogg', 'sound/Lazerhawk.mp3']

lvls = []
for i in range(2, 10):
    lvls.append(10 ** i)
lvls = lvls[::-1]

drop_velocities = [6, 6, 6]


def image_name_to_path(name):
    return 'images/' + name + '.png'


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((100, SPRITE_HEIGHT))
        self.rect = self.surf.get_rect()
        self.rect.y = SCREEN_HEIGHT - self.rect.height
        self.velocity = 10
        self.left = None
        self.right = None

    def skin(self, image_name):
        self.left = pygame.image.load(image_name_to_path(image_name))
        self.right = pygame.image.load(image_name_to_path(image_name + '_right'))
        self.surf = self.left
        self.rect.size = self.surf.get_rect().size

    def update(self, pressed_keys):
        if pressed_keys[K_w]:
            self.rect.move_ip(0, - self.velocity)
        if pressed_keys[K_s]:
            self.rect.move_ip(0, self.velocity)
        if pressed_keys[K_a]:
            self.rect.move_ip(- self.velocity, 0)
            self.surf = self.left
        if pressed_keys[K_d]:
            self.rect.move_ip(self.velocity, 0)
            self.surf = self.right
        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Resource(pygame.sprite.Sprite):

    def __init__(self):
        super(Resource, self).__init__()
        self.surf = pygame.Surface((100, SPRITE_HEIGHT))
        self.rect = self.surf.get_rect()
        self.amount = 0
        self.random_position(1)

    def skin(self, image_name):
        self.surf = pygame.image.load(image_name_to_path(image_name))
        self.rect.size = self.surf.get_rect().size

    def random_position(self, _factor):
        self.amount = 10 * _factor
        x = random.randint(0, SCREEN_WIDTH - self.rect.width) - self.rect.x
        y = random.randint(200, SCREEN_HEIGHT - self.rect.height) - self.rect.y
        self.rect.move_ip(x, y)

    def shrink_by(self, _factor):
        self.amount -= _factor
        if self.amount <= 0:
            self.random_position(_factor)


class Drop(pygame.sprite.Sprite):

    def __init__(self):
        super(Drop, self).__init__()
        self.surf = pygame.Surface((100, SPRITE_HEIGHT))
        self.bonus = False
        self.rect = self.surf.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH)
        self.velocity = 7
        self.normal_skin = None
        self.bonus_skin = None

    def skin(self, image_name):
        self.normal_skin = pygame.image.load(image_name_to_path(image_name))
        self.bonus_skin = pygame.image.load(image_name_to_path(image_name + '_bonus'))
        if self.bonus:
            self.surf = self.bonus_skin
        else:
            self.surf = self.normal_skin
        self.rect.size = self.surf.get_rect().size

    def update(self):
        self.rect.move_ip(0, self.velocity)
        if self.rect.y >= SCREEN_HEIGHT:
            self.spawn()

    def spawn(self):
        self.bonus = random.random() < BONUS_CHANCE
        if self.bonus:
            self.surf = self.bonus_skin
            self.rect = self.surf.get_rect()
        else:
            self.surf = self.normal_skin
            self.rect = self.surf.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = 0


class Button(pygame.sprite.Sprite):
    def __init__(self, label):
        super(Button, self).__init__()
        self.font = pygame.font.SysFont(None, 72)
        self.score_text = self.font.render(label, True, BLUE)
        self.surf = pygame.Surface(self.score_text.get_rect().size)
        self.rect = self.surf.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.y = SCREEN_HEIGHT / 2
        self.surf.fill((255, 255, 255))
        self.label = label


class LevelBar(pygame.sprite.Sprite):
    def __init__(self):
        super(LevelBar, self).__init__()
        self.surf = pygame.Surface((0, 50))
        self.rect = self.surf.get_rect()
        self.rect.y = 20
        self.rect.x = 20
        self.surf.fill((0, 255, 0))

    def update(self, _score, _level_up):
        self.surf = pygame.Surface((200 * _score / _level_up, 50))
        self.surf.fill((0, 255, 0))


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.level = 0
        self.score = None
        self.highscore = 0
        self.factor = 1
        self.player = Player()
        self.resource = Resource()
        self.drop = Drop()
        self.levelBar = LevelBar()
        self.level_ups = lvls
        self.font = pygame.font.SysFont(None, 72)
        self.background = None
        self.running = None
        self.star = pygame.image.load('images/hit.png')

    def level_up(self):
        if self.level < len(background_names):
            pygame.mixer.music.load(music_names[self.level])
            pygame.mixer.music.play()
            self.background = pygame.image.load(image_name_to_path(background_names[self.level]))
            self.player.skin(player_names[self.level])
            self.resource.skin(resource_names[self.level])
            self.drop.skin(drop_names[self.level])
        else:
            background_rand = random.randint(0, len(background_names) - 1)
            self.background = pygame.image.load(image_name_to_path(background_names[background_rand]))
            player_rand = random.randint(0, len(player_names) - 1)
            self.player.skin(player_names[player_rand])
            resource_rand = random.randint(0, len(resource_names) - 1)
            self.resource.skin(resource_names[resource_rand])
            drop_rand = random.randint(0, len(drop_names) - 1)
            self.drop.skin(drop_names[drop_rand])
        self.level += 1

    def click(self):
        if self.player.rect.colliderect(self.resource.rect):
            self.score += self.factor
            self.resource.shrink_by(self.factor)
            self.levelBar.update(self.score, self.level_ups[-1])
            return 5
        else:
            return 0

    def hit(self):
        if self.player.rect.colliderect(self.drop.rect):
            if self.drop.bonus:
                self.factor *= 2
            else:
                self.score -= 10 * self.factor
            self.drop.spawn()

    def show(self, clicked):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.levelBar.surf, self.levelBar.rect)
        level_bar_text = self.font.render(str(f'Level {self.level}'), True, BLUE)
        self.screen.blit(level_bar_text, self.levelBar.rect, )
        self.screen.blit(self.resource.surf, self.resource.rect)
        self.screen.blit(self.player.surf, self.player.rect)
        self.screen.blit(self.drop.surf, self.drop.rect)
        if clicked:
            x = self.player.rect.centerx / 2 + self.resource.rect.centerx / 2 - self.star.get_width() / 2
            y = self.player.rect.centery / 2 + self.resource.rect.centery / 2 - self.star.get_height() / 2
            self.screen.blit(self.star, (x, y))
        score_text = self.font.render(str(f'{self.score:,}'), True, BLUE)
        self.screen.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_rect().width / 2, 20), )

        pygame.display.flip()

    def score_update(self):
        self.highscore = max(self.score, self.highscore)
        if self.score >= self.level_ups[-1]:
            self.level_up()
            self.level_ups.pop()
            self.levelBar.update(self.score, self.level_ups[-1])
        if self.score < 0:
            self.running = False
            self.menu()

    def run(self):
        self.score = 30
        self.level_ups = lvls
        self.level = 0
        self.level_up()
        self.factor = 1
        self.running = True
        self.levelBar.update(self.score, self.level_ups[-1])
        click_timer = 0
        clock = pygame.time.Clock()
        while self.running:

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                        self.menu()

                elif event.type == QUIT:
                    self.running = False
                    pygame.display.quit()
                    pygame.quit()
                    exit()

                if event.type == MOUSEBUTTONUP:
                    pygame.mouse.get_pos()
                    click_timer = self.click()

            self.player.update(pygame.key.get_pressed())
            self.drop.update()
            self.hit()
            self.score_update()
            clicked = click_timer > 0
            self.show(clicked)
            if clicked:
                click_timer -= 1

            clock.tick(60)

    def menu(self):
        pygame.mixer.music.load('sound/Tristram.ogg')
        pygame.mixer.music.play()
        self.running = True
        clock = pygame.time.Clock()
        start_button = Button('Start')
        menu_background = pygame.image.load(image_name_to_path('menu_background'))
        while self.running:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()

                    if start_button.rect.collidepoint(pos):
                        self.running = False
                        self.run()

                elif event.type == QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    exit()

            self.screen.blit(menu_background, (0, 0))
            self.screen.blit(start_button.surf, start_button.rect)
            start_text = self.font.render(start_button.label, True, BLUE)
            self.screen.blit(start_text, start_button.rect)

            instruction_text = self.font.render('W, A, S, D + Maus.', True, BLUE)
            self.screen.blit(instruction_text, (SCREEN_WIDTH / 2 - instruction_text.get_rect().width / 2, 500))
            if self.highscore:
                highscore_text = self.font.render('Highscore: ' + str(self.highscore), True, BLUE)
                self.screen.blit(highscore_text, (SCREEN_WIDTH / 2 - highscore_text.get_rect().width / 2, 300))
            pygame.display.flip()

            clock.tick(60)


game = Game()
game.menu()
