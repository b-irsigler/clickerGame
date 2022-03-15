import pygame
import random
from pygame.locals import (K_w, K_a, K_s, K_d, MOUSEBUTTONUP, K_ESCAPE, KEYDOWN, QUIT, )

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

SPRITE_HEIGHT = 200

factor = 1
game = 1
score = 30
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BONUS_CHANCE = .1

background_names = ['lionking_background', 'ruegenwalder_background', 'synthwave_background']
player_names = ['lionking_player', 'ruegenwalder_player', 'synthwave_player']
resource_names = ['lionking_resource', 'ruegenwalder_resource', 'synthwave_resource']
drop_names = ['lionking_drop', 'ruegenwalder_drop', 'synthwave_drop']

level_ups = [0, 100, 1000]
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


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.level = 0
        self.score = 30
        self.factor = 1
        self.player = Player()
        self.resource = Resource()
        self.drop = Drop()
        self.font = pygame.font.SysFont(None, 72)

    def level_up(self):
        self.background = pygame.image.load(image_name_to_path(background_names[self.level]))
        self.player.skin(player_names[self.level])
        self.resource.skin(resource_names[self.level])
        self.drop.skin(drop_names[self.level])
        self.level += 1

    def click(self):
        if self.player.rect.colliderect(self.resource.rect):
            self.score += self.factor
            self.resource.shrink_by(self.factor)

    def hit(self):
        if self.player.rect.colliderect(self.drop.rect):
            if self.drop.bonus:
                self.factor *= 2
            else:
                self.score -= 10 * self.factor
            self.drop.spawn()

    def show(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.resource.surf, self.resource.rect)
        self.screen.blit(self.player.surf, self.player.rect)
        self.screen.blit(self.drop.surf, self.drop.rect)
        score_text = self.font.render(str(f'{self.score:,}'), True, BLUE)
        self.screen.blit(score_text, (SCREEN_WIDTH / 2 - score_text.get_rect().width / 2, 20), )
        pygame.display.flip()

    def level_or_loose(self):
        if self.level == 1 and self.score >= level_ups[self.level]:
        #if level_ups[self.level] <= self.score:
            self.level_up()
        if self.score < 0:
            self.running = False

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        while self.running:

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    self.running = False

                if event.type == MOUSEBUTTONUP:
                    pygame.mouse.get_pos()
                    self.click()

            self.player.update(pygame.key.get_pressed())
            self.drop.update()
            self.hit()
            self.level_or_loose()
            self.show()

            clock.tick(60)


game = Game()
game.level_up()
game.run()
