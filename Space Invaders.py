# -*- coding: utf-8 -*-
import pygame
import random
import sys
import schedule

pygame.init()

difficult = 1
players = 1
hp1 = 100
hp2 = 100
count_deaths = 0
count_asteroids_1 = 0
count_asteroids_2 = 0
asteroids_count = 0

def terminate():
    pygame.quit()
    sys.exit()

def closing():
    pygame.quit()
    sys.exit()
    schedule.CancelJob

def close_game():
    schedule.every(5).seconds.do(closing)

    while True:
        schedule.run_pending()   

def pause():
    paused = True
    
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                
        pygame.init()
        
        font_type = pygame.font.Font('font.otf', 50)
        screen = pygame.display.set_mode()
        
        fon = pygame.transform.scale(load_image('Space.jpg'), (1000, 700))
        screen.blit(fon, (0, 0))
        
        text1 = font_type.render('Paused. Press Left Shift to continue.', True, (255, 255, 255))
        screen.blit(text1, (10, 10))   
        
        text2 = font_type.render('To go out, press Q.', True, (255, 255, 255))
        screen.blit(text2, (10, 100))
        
        text3 = font_type.render('To return to main menu press Escape.', True, (255, 255, 255))
        screen.blit(text3, (10, 190))        
        
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            paused = False
            
        elif pygame.key.get_pressed()[pygame.K_q]:
            terminate()
        
        elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
            pygame.quit()
            start_screen()
    
        pygame.display.update()

shoot_sound = pygame.mixer.Sound('Bluster.ogg')
menu_music = pygame.mixer.Sound('music.ogg')
game_music = pygame.mixer.Sound('pesnya.ogg')
avariya = pygame.mixer.Sound('avariya.ogg')
alarming = pygame.mixer.Sound('alarm.ogg')
win = pygame.mixer.Sound('win.ogg')
loose = pygame.mixer.Sound('game_over.ogg')

icon = pygame.image.load('logo.png')
pygame.display.set_icon(icon)

def load_image(filename):
    return pygame.image.load(filename).convert_alpha()

def rotate_image_by_center(image, angle):
    original_rect = image.get_rect()
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = original_rect.copy()
    rotated_rect.center = rotated_image.get_rect().center
    rotated_image = rotated_image.subsurface(rotated_rect).copy()

    return rotated_image                


class Asteroid(pygame.sprite.Sprite):
    image = None

    def __init__(self, location, *groups):
        super(Asteroid, self).__init__(*groups)

        self.position = list(location)
        self.velocity = 0
        self.direction = pygame.math.Vector2(0, 0)

        self.rect = pygame.rect.Rect(self.position, self.image.get_size())


    def update(self, delta_time, game_world):
        
        for axis in (0, 1):
            delta_by_axis = self.velocity * self.direction[axis] * delta_time
            self.position[axis] += delta_by_axis
            self.position[axis] %= game_world.size[axis]
        self.rect.center = self.position
        self.velocity *= 0.98


class Bullet(pygame.sprite.Sprite):
    image = None
    lifespan = None

    def __init__(self, location, start_velocity, direction, *groups):
        super(Bullet, self).__init__(*groups)

        self.direction = direction
        self.velocity = start_velocity + 300
        self.lifespan = self.lifespan
        self.position = list(location)

        self.rect = pygame.rect.Rect(location, self.image.get_size())

    def update(self, delta_time, game_world):
        self.lifespan -= delta_time
        if self.lifespan < 0:
            self.kill()

        for axis in (0, 1):
            delta_by_axis = self.velocity * self.direction[axis] * delta_time
            self.position[axis] += delta_by_axis
            self.position[axis] %= game_world.size[axis]
        self.rect.center = self.position

        if pygame.sprite.spritecollide(self, game_world.asteroids, True):
            self.kill()
            global count_asteroids_1
            count_asteroids_1 += 1
            global asteroids_count
            asteroids_count -= 1


class Bullet_Sec(pygame.sprite.Sprite):
    image = None
    lifespan = None

    def __init__(self, location, start_velocity, direction, *groups):
        super(Bullet_Sec, self).__init__(*groups)

        self.direction = direction
        self.velocity = start_velocity + 300
        self.lifespan = self.lifespan
        self.position = list(location)

        self.rect = pygame.rect.Rect(location, self.image.get_size())

    def update(self, delta_time, game_world):
        self.lifespan -= delta_time
        if self.lifespan < 0:
            self.kill()

        for axis in (0, 1):
            delta_by_axis = self.velocity * self.direction[axis] * delta_time
            self.position[axis] += delta_by_axis
            self.position[axis] %= game_world.size[axis]
        self.rect.center = self.position

        if pygame.sprite.spritecollide(self, game_world.asteroids, True):
            self.kill()
            global count_asteroids_2
            count_asteroids_2 += 1
            global asteroids_count
            asteroids_count -= 1
    

class SpaceShip(pygame.sprite.Sprite):
    engine_off = None
    engine_on = None
    gun_cooldown_time = None

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.original_image = self.engine_off

        self.image = self.original_image
        self.rect = pygame.rect.Rect(location, self.image.get_size())

        self.velocity = 0
        self.direction = pygame.math.Vector2(1, 0)
        self.rotate_at = 3
        self.position = list(location)

        self.is_engine_working = False
        self.rotating_clockwise = False
        self.rotating_counterclockwise = False
        self.firing = False
        self.gun_cooldown = 0
        
        global hp1
        self.hp = hp1 = 100

    def update(self, delta_time, game_world):

        if self.rotating_counterclockwise:
            self.direction = self.direction.rotate(-self.rotate_at)
        if self.rotating_clockwise:
            self.direction = self.direction.rotate(self.rotate_at)
        rotate_at = self.direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = rotate_image_by_center(self.original_image, rotate_at)


        if self.is_engine_working:
            self.velocity += 20
        self.velocity *= 0.95

        for axis in (0, 1):
            delta_by_axis = self.velocity * self.direction[axis] * delta_time
            self.position[axis] += delta_by_axis
            self.position[axis] %= game_world.size[axis]
        self.rect.center = self.position

        if self.firing and not self.gun_cooldown:
            point = (self.rect.center[0] + self.direction[0] * 21 / 2,
                     self.rect.center[1] + self.direction[1] * 21 / 2)
            Bullet(point, self.velocity, self.direction, game_world.sprites)
            self.gun_cooldown = self.gun_cooldown_time
        self.gun_cooldown = max(0, self.gun_cooldown - delta_time)
        
        if pygame.sprite.spritecollide(self, game_world.asteroids, True):
            self.hp -= 10
            global hp1
            global count_deaths
            hp1 -= 10
            global asteroids_count
            asteroids_count -= 1            
            avariya.play()
            if self.hp <= 0:
                self.kill()
                count_deaths += 1
            elif self.hp == 30:
                alarming.play()

    def turn_engine(self, state):
        self.is_engine_working = state
        if self.is_engine_working:
            self.original_image = self.engine_on
        else:
            self.original_image = self.engine_off

    def rotate_clockwise(self, state):
        self.rotating_clockwise = state

    def rotate_counterclockwise(self, state):
        self.rotating_counterclockwise = state

    def fire(self, state):
        shoot_sound.play()
        self.firing = state


class SpaceShipSecPlayer(pygame.sprite.Sprite):
    engine_off = None
    engine_on = None
    gun_cooldown_time = None

    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.original_image = self.engine_off

        self.image = self.original_image
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        

        self.velocity1 = 0
        self.direction = pygame.math.Vector2(1, 0)
        self.rotate_at = 3
        self.position = list(location)

        self.is_engine_working = False
        self.rotating_clockwise = False
        self.rotating_counterclockwise = False
        self.firing = False
        self.gun_cooldown = 0
        
        global hp2
        self.hp2 = hp2 = 100

    def update(self, delta_time, game_world):

        if self.rotating_counterclockwise:
            self.direction = self.direction.rotate(-self.rotate_at)
        if self.rotating_clockwise:
            self.direction = self.direction.rotate(self.rotate_at)
        rotate_at = self.direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = rotate_image_by_center(self.original_image, rotate_at)


        if self.is_engine_working:
            self.velocity1 += 20
        self.velocity1 *= 0.95

        for axis in (0, 1):
            delta_by_axis = self.velocity1 * self.direction[axis] * delta_time
            self.position[axis] += delta_by_axis
            self.position[axis] %= game_world.size[axis]
        self.rect.center = self.position

        if self.firing and not self.gun_cooldown:
            point = (self.rect.center[0] + self.direction[0] * 21 / 2,
                     self.rect.center[1] + self.direction[1] * 21 / 2)
            Bullet_Sec(point, self.velocity1, self.direction, game_world.sprites)
            self.gun_cooldown = self.gun_cooldown_time
        self.gun_cooldown = max(0, self.gun_cooldown - delta_time)
        
        if pygame.sprite.spritecollide(self, game_world.asteroids, True):
            self.hp2 -= 10
            global hp2
            global count_deaths
            hp2 -= 10
            global asteroids_count
            asteroids_count -= 1            
            avariya.play()
            if self.hp2 <= 0:
                self.kill()
                count_deaths += 1
            elif self.hp2 == 30:
                alarming.play()

    def turn_engine(self, state):
        self.is_engine_working = state
        if self.is_engine_working:
            self.original_image = self.engine_on
        else:
            self.original_image = self.engine_off

    def rotate_clockwise(self, state):
        self.rotating_clockwise = state

    def rotate_counterclockwise(self, state):
        self.rotating_counterclockwise = state

    def fire(self, state):
        shoot_sound.play()
        self.firing = state


class GameWorld(object):
    def __init__(self, display_surface, config):
        self.fps = 60
        self.display_surface = display_surface
        self.size = self.display_surface.get_size()
        
        self.fon = pygame.transform.scale(load_image('kosmos.jpg'), (1000, 700))

        self.sprites = pygame.sprite.Group()
        self.spaceship = SpaceShip((100, 100), self.sprites)
        
        if players == 2:
            self.spaceship2 = SpaceShipSecPlayer((500, 500), self.sprites)

        self.asteroids = pygame.sprite.Group()
        
        for i in range(config['game_world']['asteroids']['count']):
            x = random.randint(0, self.size[0])
            y = random.randint(0, self.size[1])
            Asteroid((x, y), self.asteroids)
        self.sprites.add(self.asteroids)
        
        pygame.init()

    def play(self):
        clock = pygame.time.Clock()
        
        if players == 2:

            actions = {
                pygame.K_w: self.spaceship.turn_engine,
                pygame.K_d: self.spaceship.rotate_clockwise,
                pygame.K_a: self.spaceship.rotate_counterclockwise,
                pygame.K_r: self.spaceship.fire,
            }
            
            actions2 = {
                pygame.K_UP: self.spaceship2.turn_engine,
                pygame.K_RIGHT: self.spaceship2.rotate_clockwise,
                pygame.K_LEFT: self.spaceship2.rotate_counterclockwise,
                pygame.K_RCTRL: self.spaceship2.fire,
            }
        else:
            actions = {
                pygame.K_w: self.spaceship.turn_engine,
                pygame.K_d: self.spaceship.rotate_clockwise,
                pygame.K_a: self.spaceship.rotate_counterclockwise,
                pygame.K_r: self.spaceship.fire,
            }            

        playing = True
        
        pygame.init()
        
        game_music.play()

        while playing:
            delta_time = clock.tick(self.fps)        

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()

                elif event.type == pygame.KEYDOWN:
                    actions.get(event.key, lambda x: None)(True)
                    
                    if players == 2:
                        actions2.get(event.key, lambda x: None)(True)

                elif event.type == pygame.KEYUP:
                    actions.get(event.key, lambda x: None)(False)
                    
                    if players == 2:
                        actions2.get(event.key, lambda x: None)(False)
                    
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    pause()

            self.sprites.update(delta_time / 1000, self)
            
            self.display_surface.blit(self.fon, (0, 0))
            self.sprites.draw(self.display_surface)
            
            font_type = pygame.font.Font('hp_font.ttf', 30)    
            
            if hp1 <= 30:
                text1 = font_type.render('PLAYER 1  ' + str(hp1), True, (255, 0, 0))
            elif hp1 > 30:
                text1 = font_type.render('PLAYER 1  ' + str(hp1), True, (255, 255, 255))
                
            self.display_surface.blit(text1, (10, 10))
            
            if players == 2:
                if hp2 <= 30:
                    text2 = font_type.render('PLAYER 2  ' + str(hp2), True, (255, 0, 0))
                elif hp2 > 30:
                    text2 = font_type.render('PLAYER 2  ' + str(hp2), True, (255, 255, 255))
                
                self.display_surface.blit(text2, (400, 10))
            
            if players == 2:
                if count_deaths == 2:
                    playing = False
                    size = WIDTH, HEIGHT = 1300, 900
                    screen = pygame.display.set_mode(size)
                    
                    loosed = True
                    
                    pygame.init()
                    
                    font_type1 = pygame.font.Font('hp_font.ttf', 80)
                    font_typef = pygame.font.Font('hp_font.ttf', 10)
                    font_type2 = pygame.font.Font('hp_font.ttf', 40)
                    
                    fon = pygame.transform.scale(load_image('texture.jpg'), (1300, 900))
                    screen.blit(fon, (0, 0))
                    
                    text1 = font_type1.render('Game Over', True, (255, 255, 255))
                    screen.blit(text1, (300, 10))
                    
                    text2 = font_type1.render('Press M to go to menu.', True, (255, 255, 255))
                    screen.blit(text2, (4, 120))
                    
                    text3 = font_type1.render('Press Q to go out.', True, (255, 255, 255))
                    screen.blit(text3, (4, 230))
                    
                    text5 = font_typef.render('Press F to pay respect.', True, (255, 255, 255))
                    screen.blit(text5, (700, 550))
                    
                    text6 = font_type2.render('Quantity of knocked down asteroids of first player: ' + str(count_asteroids_1), True, (255, 255, 255))
                    screen.blit(text6, (5, 450))
                    
                    text7 = font_type2.render('Quantity of knocked down asteroids of second player: ' + str(count_asteroids_2), True, (255, 255, 255))
                    screen.blit(text7, (5, 560))
                    
                    text8 = font_type1.render('YOU DIED, LOOOOOOOSERS!', True, (255, 255, 255))
                    screen.blit(text8, (5, 670))
                    
                    loose.play()
                    
                    while loosed:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                terminate()
                                
                            elif pygame.key.get_pressed()[pygame.K_m]:
                                start_screen()
                                
                            elif pygame.key.get_pressed()[pygame.K_q]:
                                terminate()
                            
                            elif pygame.key.get_pressed()[pygame.K_f]:
                                close_game()
                        
                        pygame.display.flip()
                elif asteroids_count == 0:
                    playing = False
                    size = WIDTH, HEIGHT = 1300, 900
                    screen = pygame.display.set_mode(size)
                    
                    loosed = True
                    
                    pygame.init()
                    
                    font_type1 = pygame.font.Font('hp_font.ttf', 80)
                    font_typef = pygame.font.Font('hp_font.ttf', 10)
                    font_type2 = pygame.font.Font('hp_font.ttf', 40)
                    font_type3 = pygame.font.Font('hp_font.ttf', 60)
                    
                    fon = pygame.transform.scale(load_image('texture.jpg'), (1300, 900))
                    screen.blit(fon, (0, 0))
                    
                    text1 = font_type3.render('CONGRATULATIONS! YOU DID NOT DIE!', True, (255, 255, 255))
                    screen.blit(text1, (10, 10))
                    
                    text2 = font_type1.render('Press M to go to menu.', True, (255, 255, 255))
                    screen.blit(text2, (4, 120))
                    
                    text3 = font_type1.render('Press Q to go out.', True, (255, 255, 255))
                    screen.blit(text3, (4, 230))
                    
                    text5 = font_typef.render('Press F to pay respect.', True, (255, 255, 255))
                    screen.blit(text5, (700, 550))
                    
                    text6 = font_type2.render('Quantity of knocked down asteroids of first player: ' + str(count_asteroids_1), True, (255, 255, 255))
                    screen.blit(text6, (5, 450))
                    
                    text7 = font_type2.render('Quantity of knocked down asteroids of second player: ' + str(count_asteroids_2), True, (255, 255, 255))
                    screen.blit(text7, (5, 560))
                    
                    if count_asteroids_1 > count_asteroids_2:
                        text8 = font_type2.render('First player wins!', True, (255, 255, 255))
                        screen.blit(text8, (5, 670))
                    else:
                        text9 = font_type2.render('Second player wins!', True, (255, 255, 255))
                        screen.blit(text9, (5, 670)) 
                    
                    win.play()
                    
                    while loosed:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                terminate()
                                
                            elif pygame.key.get_pressed()[pygame.K_m]:
                                start_screen()
                                
                            elif pygame.key.get_pressed()[pygame.K_q]:
                                terminate()
                            
                            elif pygame.key.get_pressed()[pygame.K_f]:
                                close_game()
                        
                        pygame.display.flip()
            else:
                if count_deaths == 1:
                    playing = False
                    size = WIDTH, HEIGHT = 1300, 900
                    screen = pygame.display.set_mode(size)
                    
                    loosed = True
                    
                    pygame.init()
                    
                    font_type1 = pygame.font.Font('hp_font.ttf', 80)
                    font_typef = pygame.font.Font('hp_font.ttf', 10)
                    font_type2 = pygame.font.Font('hp_font.ttf', 40)
                    
                    fon = pygame.transform.scale(load_image('texture.jpg'), (1300, 900))
                    screen.blit(fon, (0, 0))
                    
                    text1 = font_type1.render('Game Over', True, (255, 255, 255))
                    screen.blit(text1, (350, 10))
                    
                    text2 = font_type1.render('Press M to go to menu.', True, (255, 255, 255))
                    screen.blit(text2, (100, 120))
                    
                    text3 = font_type1.render('Press Q to go out.', True, (255, 255, 255))
                    screen.blit(text3, (100, 230))
                    
                    text5 = font_typef.render('Press F to pay respect.', True, (255, 255, 255))
                    screen.blit(text5, (700, 700))
                    
                    text6 = font_type2.render('Quantity of knocked down asteroids of player: ' + str(count_asteroids_1), True, (255, 255, 255))
                    screen.blit(text6, (5, 450))
                    
                    loose.play()
                    
                    while loosed:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                terminate()
                                
                            elif pygame.key.get_pressed()[pygame.K_m]:
                                start_screen()
                                
                            elif pygame.key.get_pressed()[pygame.K_q]:
                                terminate()
                            
                            elif pygame.key.get_pressed()[pygame.K_f]:
                                close_game()
                        
                        pygame.display.flip()
                elif asteroids_count == 0:
                    playing = False
                    size = WIDTH, HEIGHT = 1300, 900
                    screen = pygame.display.set_mode(size)
                    
                    loosed = True
                    
                    pygame.init()
                    
                    font_type1 = pygame.font.Font('hp_font.ttf', 80)
                    font_typef = pygame.font.Font('hp_font.ttf', 10)
                    font_type2 = pygame.font.Font('hp_font.ttf', 40)
                    font_type3 = pygame.font.Font('hp_font.ttf', 60)
                    
                    fon = pygame.transform.scale(load_image('texture.jpg'), (1300, 900))
                    screen.blit(fon, (0, 0))
                    
                    text1 = font_type3.render('CONGRATULATIONS! YOU ARE A WINNER!', True, (255, 255, 255))
                    screen.blit(text1, (10, 10))
                    
                    text2 = font_type1.render('Press M to go to menu.', True, (255, 255, 255))
                    screen.blit(text2, (4, 120))
                    
                    text3 = font_type1.render('Press Q to go out.', True, (255, 255, 255))
                    screen.blit(text3, (4, 230))
                    
                    text5 = font_typef.render('Press F to pay respect.', True, (255, 255, 255))
                    screen.blit(text5, (700, 550))
                    
                    text6 = font_type2.render('Quantity of knocked down asteroids of player: ' + str(count_asteroids_1), True, (255, 255, 255))
                    screen.blit(text6, (5, 450))
                    
                    win.play()
                    
                    while loosed:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                terminate()
                                
                            elif pygame.key.get_pressed()[pygame.K_m]:
                                start_screen()
                                
                            elif pygame.key.get_pressed()[pygame.K_q]:
                                terminate()
                            
                            elif pygame.key.get_pressed()[pygame.K_f]:
                                close_game()
                        
                        pygame.display.flip()                   
                
            pygame.display.flip()


def create_game_world():
    global asteroids_count
    global count_deaths 
    global count_asteroids_1 
    global count_asteroids_2
    count_deaths = 0
    count_asteroids_1 = 0
    count_asteroids_2 = 0
    
    if players == 2:
        if difficult == 1:
            
            config = {
                'window': {'size': (1000, 700), 'caption': 'Space Invaders'},
                'game_world': {
                    'spaceship': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 0.01,
                    },
                    'spaceship2': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 0.01,
                    },                
                    'asteroids': {
                        'count': 20,
                        'image': 'enemy.png',
                    },
                    'bullet': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },
                    'bullet2': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },                    
                }
            }
        elif difficult == 2:
            
            config = {
                'window': {'size': (1000, 700), 'caption': 'Space Invaders'},
                'game_world': {
                    'spaceship': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 0.6,
                    },
                    'spaceship2': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 0.6,
                    },                
                    'asteroids': {
                        'count': 40,
                        'image': 'enemy.png',
                    },
                    'bullet': {
                        'lifespan': 3,
                        'image': 'bullet.png',
                    },
                    'bullet2': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },                    
                }
            }
        else:
            
            config = {
                'window': {'size': (1000, 700), 'caption': 'Space Invaders'},
                'game_world': {
                    'spaceship': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 1,
                    },
                    'spaceship2': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 1,
                    },                
                    'asteroids': {
                        'count': 60,
                        'image': 'enemy.png',
                    },
                    'bullet': {
                        'lifespan': 0.5,
                        'image': 'bullet.png',
                    },
                    'bullet2': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },                    
                }
            }        
        
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
        
        display_surface = pygame.display.set_mode(config['window']['size'])
        pygame.display.set_caption(config['window']['caption'])
        
        Bullet.image = load_image(config['game_world']['bullet']['image'])
        Bullet.lifespan = config['game_world']['bullet']['lifespan']
        
        Bullet_Sec.image = load_image(config['game_world']['bullet2']['image'])
        Bullet_Sec.lifespan = config['game_world']['bullet2']['lifespan']        
        
        Asteroid.image = load_image(config['game_world']['asteroids']['image'])
        
        SpaceShip.engine_off = load_image(config['game_world']['spaceship']['image_engine_off'])
        SpaceShip.engine_on = load_image(config['game_world']['spaceship']['image_engine_on'])
        SpaceShip.gun_cooldown_time = config['game_world']['spaceship']['gun_cooldown_time']
        
        SpaceShipSecPlayer.engine_off = load_image(config['game_world']['spaceship2']['image_engine_off'])
        SpaceShipSecPlayer.engine_on = load_image(config['game_world']['spaceship2']['image_engine_on'])
        SpaceShipSecPlayer.gun_cooldown_time = config['game_world']['spaceship2']['gun_cooldown_time']
        
    else:
        if difficult == 1:
            
            config = {
                'window': {'size': (1000, 700), 'caption': 'Space Invaders'},
                'game_world': {
                    'spaceship': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 0.01,
                    },               
                    'asteroids': {
                        'count': 10,
                        'image': 'enemy.png',
                    },
                    'bullet': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },
                    'bullet2': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },                    
                }
            }
        elif difficult == 2:
            
            config = {
                'window': {'size': (1000, 700), 'caption': 'Space Invaders'},
                'game_world': {
                    'spaceship': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 0.6,
                    },                
                    'asteroids': {
                        'count': 30,
                        'image': 'enemy.png',
                    },
                    'bullet': {
                        'lifespan': 3,
                        'image': 'bullet.png',
                    },
                    'bullet2': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },                    
                }
            }
        else:
            
            config = {
                'window': {'size': (1000, 700), 'caption': 'Space Invaders'},
                'game_world': {
                    'spaceship': {
                        'image_engine_on': 'ship_on.png',
                        'image_engine_off': 'ship_off.png',
                        'gun_cooldown_time': 1,
                    },               
                    'asteroids': {
                        'count': 60,
                        'image': 'enemy.png',
                    },
                    'bullet': {
                        'lifespan': 0.5,
                        'image': 'bullet.png',
                    },
                    'bullet2': {
                        'lifespan': 5,
                        'image': 'bullet.png',
                    },
                }
            }        
        
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
        
        display_surface = pygame.display.set_mode(config['window']['size'])
        pygame.display.set_caption(config['window']['caption'])
        
        Bullet.image = load_image(config['game_world']['bullet']['image'])
        Bullet.lifespan = config['game_world']['bullet']['lifespan']        
        
        Asteroid.image = load_image(config['game_world']['asteroids']['image'])
        
        SpaceShip.engine_off = load_image(config['game_world']['spaceship']['image_engine_off'])
        SpaceShip.engine_on = load_image(config['game_world']['spaceship']['image_engine_on'])
        SpaceShip.gun_cooldown_time = config['game_world']['spaceship']['gun_cooldown_time']
    
    game_world = GameWorld(display_surface, config)
    asteroids_count = config['game_world']['asteroids']['count']
    game_world.play()

def select_num_of_players():
    size = WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode(size)
    
    pygame.init()
    
    fon = pygame.transform.scale(load_image('kosmos_player.jpg'), (1000, 600))
    screen.blit(fon, (0, 0))
    
    global players
    
    font_type1 = pygame.font.Font('players_font.ttf', 70)
    font_type2 = pygame.font.Font('players_font.ttf', 45)
    
    text1 = font_type1.render('Number of players selection', True, (255, 255, 255))
    screen.blit(text1, (100, 10))
    
    text2 = font_type2.render('To select number of players, press keys "1" or "2".', True, (255, 255, 255))
    screen.blit(text2, (20, 375))
    
    selected = True     
    
    while selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                
            elif pygame.key.get_pressed()[pygame.K_1]:
                players = 1
                selected = False
            elif pygame.key.get_pressed()[pygame.K_2]:
                players = 2
                selected = False
                
        pygame.display.flip()
        
    start_screen()    

def select_difficult():
    size = WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode(size)
    
    pygame.init()
    
    global difficult
    
    fon = pygame.transform.scale(load_image('difficult.jpg'), (1000, 700))
    screen.blit(fon, (0, 0)) 
    
    font_type1 = pygame.font.Font('fonts.ttf', 70)
    font_type2 = pygame.font.Font('fonts.ttf', 45)
    
    text1 = font_type1.render('Difficulty selection', True, (255, 255, 255))
    screen.blit(text1, (200, 10))
    
    text2 = font_type2.render('To select level of difficulty,', True, (255, 255, 255))
    screen.blit(text2, (20, 100))
    
    text3 = font_type2.render('press "1", "2" or "3" num keys.', True, (255, 255, 255))
    screen.blit(text3, (300, 140))
    
    text4 = font_type1.render("What's the difference? ", True, (255, 255, 255))
    screen.blit(text4, (0, 200))
    
    text5 = font_type2.render("Gun Cooldown time,", True, (255, 255, 255))
    screen.blit(text5, (20, 400))
    
    text6 = font_type2.render("quantity of asteroids", True, (255, 255, 255))
    screen.blit(text6, (20, 440))
    
    text7 = font_type2.render("and lifespan of bullets.", True, (255, 255, 255))
    screen.blit(text7, (20, 480))     
    
    selected = True     
    
    while selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                
            elif pygame.key.get_pressed()[pygame.K_1]:
                difficult = 1
                selected = False
            elif pygame.key.get_pressed()[pygame.K_2]:
                difficult = 2
                selected = False
            elif pygame.key.get_pressed()[pygame.K_3]:
                difficult = 3
                selected = False
                
        pygame.display.flip()
        
    start_screen()

def rules():
    size = WIDTH, HEIGHT = 1000, 600
    screen = pygame.display.set_mode(size)
    
    pygame.init()
    
    font_type1 = pygame.font.Font('rules_font.ttf', 80)
    font_type2 = pygame.font.Font('rules_font.ttf', 30)
    
    fon = pygame.transform.scale(load_image('pause_pict.jpg'), (1000, 600))
    screen.blit(fon, (0, 0))
    
    text1 = font_type1.render('RULES', True, (255, 255, 255))
    screen.blit(text1, (400, 10))
    
    text2 = font_type2.render('There are one to two spacecrafts.', True, (255, 255, 255))
    screen.blit(text2, (20, 100))
    
    text3 = font_type2.render('Each player has an opportunity to control one of them.', True, (255, 255, 255))
    screen.blit(text3, (20, 190))
    
    text4 = font_type2.render('Controlling materializes by using keyboard.', True, (255, 255, 255))
    screen.blit(text4, (20, 330))
    
    text5 = font_type2.render('First player uses "W", "A", "D" to move and "R" to fire.', True, (255, 255, 255))
    screen.blit(text5, (20, 370))
    
    text6 = font_type2.render('Second player uses arrows to move and "RCTRL" to fire.', True, (255, 255, 255))
    screen.blit(text6, (20, 410))
    
    text7 = font_type2.render('To pause the game press "Escape".', True, (255, 255, 255))
    screen.blit(text7, (20, 450))    
    
    text8 = font_type2.render('To return to main menu press "Escape".', True, (255, 255, 255))
    screen.blit(text8, (20, 490))
    
    text8 = font_type2.render('ATTENTION! Level of difficulty = 1 by default.', True, (255, 255, 255))
    screen.blit(text8, (20, 530))    
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                
            elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                start_screen()
                
        pygame.display.flip()

def start_screen():
    
    size = WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode(size)
    
    pygame.init()
    
    menu_music.play()
    
    fon = pygame.transform.scale(load_image('menu_pict.jpg'), (1000, 700))
    screen.blit(fon, (0, 0))
    
    font_type_capture = pygame.font.Font('menu_font.ttf', 60)
    font_type = pygame.font.Font('menu_font.ttf', 50)
    
    text1 = font_type_capture.render('Space Invaders.', True, (255, 255, 255))
    screen.blit(text1, (350, 10))
    
    text2 = font_type.render('To see rules press H.', True, (255, 255, 255))
    screen.blit(text2, (50, 90))
    
    text3 = font_type.render('To exit press Q.', True, (255, 255, 255))
    screen.blit(text3, (350, 160))
    
    text4 = font_type.render('To select level of difficulty', True, (255, 255, 255))
    screen.blit(text4, (300, 220))
    
    text5 = font_type.render('press K.', True, (255, 255, 255))
    screen.blit(text5, (700, 280))
    
    text7 = font_type.render('Press N to select number of players.', True, (255, 255, 255))
    screen.blit(text7, (10, 400))
    
    text8 = font_type.render('Press P to go out.', True, (255, 255, 255))
    screen.blit(text8, (10, 500))    
    
    text6 = font_type.render('To start game press random Mouse Button.', True, (255, 255, 255))
    screen.blit(text6, (10, 600))   
    
    FPS = 60     
    
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                create_game_world()
            
            elif pygame.key.get_pressed()[pygame.K_h]:
                rules()
                    
            elif pygame.key.get_pressed()[pygame.K_q]:
                terminate()
            
            elif pygame.key.get_pressed()[pygame.K_k]:
                select_difficult()
            
            elif pygame.key.get_pressed()[pygame.K_n]:
                select_num_of_players()
            
            elif pygame.key.get_pressed()[pygame.K_p]:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()
        clock.tick(FPS)

start_screen()
terminate()