import pygame, math;
from random import randint;

"""Contains classes and helper functions used in the game."""



def get_angle(angle):
    """ gets the angle the player or the enemy should be facing """
    if angle < 0: angle = 360 + angle;
    if 45 < angle <= 135: angle = 90;
    elif 135 < angle <= 225: angle = 180;
    elif 225 < angle <= 315: angle = 270;
    elif 315 < angle <= 360 or 0 < angle < 45: angle = 0;
    return angle;

def rotate(sprite, dx, dy, angle, image):
    """ rotates an image by angle """
    rotated_image = pygame.transform.rotate(image, angle);
    sprite.rect = rotated_image.get_rect(center=sprite.rect.center);
    sprite.image = pygame.transform.scale(sprite.image, (sprite.rect.width, sprite.rect.height));
    return rotated_image;


class Entity(pygame.sprite.Sprite):

    """ Base class for game entities """

    def __init__(self, groups):
        pygame.sprite.Sprite.__init__(self);
        self.add(*groups);

    def wall_collide(self, walls, target, x_vel, y_vel):
        """ check for collisions with the walls """
        for w in walls:
            if pygame.sprite.collide_rect(target, w):
                if x_vel > 0:
                    target.rect.right = w.rect.left;
                elif x_vel < 0:
                    target.rect.left = w.rect.right;
                if y_vel > 0:
                    target.rect.bottom = w.rect.top;
                elif y_vel < 0:
                    target.rect.top = w.rect.bottom;

    def update(self, *args):
        """ to be overridden by subclasses """
        pass;


class Player(Entity):

    """ The player that the user controls """

    def __init__(self, groups, pos, background):
        Entity.__init__(self, groups);

        self.width, self.height = 32, 32;
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32);
        self.rect = self.image.get_rect();
        self.rect.x, self.rect.y = pos;
        self.x_vel, self.y_vel = 0, 0;
        self.moving = False;
        self.shooting = False;

        self.gems, self.xp = 0, 0;
        self.level = 1;
        self.weapon_active = False;
        self.speed = 14;
        self.bullets = pygame.sprite.Group();

        self.background = background;

    def move(self, walls, mouse_x, mouse_y, dx, dy):
        """ move the player towards the cursor """
        distance = math.hypot(dx, dy);
        if self.rect.collidepoint((mouse_x, mouse_y)):
            self.rect.centerx = mouse_x;
            self.rect.centery = mouse_y;
            self.x_vel, self.y_vel = 0, 0;
        elif distance:
            dx /= distance;
            dy /= distance;
            self.x_vel = -(dx * self.speed);
            self.y_vel = -(dy * self.speed);

        self.rect.x += self.x_vel;
        self.wall_collide(walls, self, self.x_vel, 0);
        self.rect.y += self.y_vel;
        self.wall_collide(walls, self, 0, self.y_vel);

    def level_up(self):
        """ level up the player """
        if self.xp >= 100:
            self.level += 1;
            self.xp = 0;

    def increase_gems(self):
        """ increase gems and points """
        self.gems += 1;
        self.xp += 10;

    def activate_weapon(self):
        """ allow the player to shoot """
        self.weapon_active = True;

    def shoot(self, mouse_pos, img):
        """ shoot bullets towards the mouse """
        if self.weapon_active and len(self.bullets.sprites()) < 1000 and self.shooting:
            Bullet([self.bullets], (self.rect.centerx, self.rect.centery), mouse_pos, img);

    def update(self, walls, mouse_pos, enemies):
        mouse_x, mouse_y = mouse_pos;
        dx, dy = self.rect.centerx - mouse_x, self.rect.centery - mouse_y;
        if self.moving:
            self.move(walls, mouse_x, mouse_y, dx, dy);
        angle = get_angle(90 - math.degrees(math.atan2(dy, dx)));
        rotated_image = rotate(self, dx, dy, angle, self.background);
        
        self.level_up();

        self.image.fill(pygame.Color(0, 0, 0, 0)); # Clear the image
        self.image.blit(rotated_image, (0, 0));

        self.bullets.update(enemies, self);


class Enemy(Entity):

    """ Tracking Banana enemy """

    def __init__(self, groups, pos, background):
        Entity.__init__(self, groups);

        self.width, self.height = 32, 32;
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32);
        self.rect = self.image.get_rect(center=pos);
        self.rect.x, self.rect.y = pos;
        self.x_vel, self.y_vel = 0, 0;
        self.speed = randint(3, 7);

        self.trigger_rect = pygame.Rect(self.rect.x-184, self.rect.y-184, 400, 400);
        self.active = False; # Once active, always active.

        self.background = background;

    def collide(self, target):
        """ check for collision with the player """
        if self.rect.colliderect(target.rect):
            target.xp -= 20;
            self.kill();

    def move(self, walls, dx, dy):
        """ move towards the player """
        distance = math.hypot(dx, dy);

        if distance:
            dx /= distance;
            dy /= distance;
            self.x_vel = -(dx * self.speed);
            self.y_vel = -(dy * self.speed);

        self.rect.x += self.x_vel;
        self.wall_collide(walls, self, self.x_vel, 0);
        self.rect.y += self.y_vel;
        self.wall_collide(walls, self, 0, self.y_vel);

    def update(self, walls, target):
        if self.active:
            dx = self.rect.x - target.rect.x;
            dy = self.rect.y - target.rect.y;

            angle = get_angle(-math.degrees(math.atan2(dy, dx)));
            rotated_image = rotate(self, dx, dy, angle, self.background);
            self.move(walls, dx, dy);
            self.collide(target)

            self.image.fill((0, 0, 0, 0));
            self.image.blit(rotated_image, (0, 0));
        else:
            if self.trigger_rect.colliderect(target.rect):
                self.active = True;
            self.image.blit(self.background, (0, 0));


class Wall(Entity):

    """ walls that serve as the boundaries and obstacles """

    def __init__(self, groups, pos, image, orientation="horizontal"):
        Entity.__init__(self, groups);

        self.width, self.height = 32, 32;
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32);
        self.rect = self.image.get_rect();
        self.rect.x, self.rect.y = pos;

        if orientation == "horizontal":
            self.background = image;
        else:
            self.background = pygame.transform.rotate(image, 90);

        self.image.blit(self.background, (0, 0));


class Scenery(Entity):

    """ For other objects in the game to make it look good """

    def __init__(self, groups, pos, img):
        Entity.__init__(self, groups);

        *_, self.width, self.height = img.get_rect();
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32);
        self.rect = self.image.get_rect();
        self.rect.x, self.rect.y = pos;
        self.image.blit(img, (0, 0));


class Item(Entity):

    """ An item that can be picked up or interacted with such as gems and guns """

    def __init__(self, groups, pos, img, function, kill=True):
        Entity.__init__(self, groups);

        *_, self.width, self.height = img.get_rect();
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32);
        self.rect = self.image.get_rect();
        self.rect.x, self.rect.y = pos;
        self.image.blit(img, (0, 0));

        self.function = function;
        self.k = kill;

    def update(self, target):
        if self.rect.colliderect(target.rect):
            self.function();
            if self.k: self.kill();


class Bullet(Entity):

    """ ^^^ it's in the name """

    def __init__(self, groups, start, end, img):
        Entity.__init__(self, groups);

        self.width, self.height = 10, 10;
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32);
        self.rect = self.image.get_rect();
        self.rect.x, self.rect.y = start;

        self.end = end;
        self.endrect = pygame.Rect(end[0]-7, end[1]-7, 15, 15)
        self.img = img;

        self.image.blit(self.img, (0, 0));

    def collide(self, targets, player):
        """ check if the bullets hit the bananas """
        if self.rect.colliderect(self.endrect): self.kill();
        for target in targets:
            if self.rect.colliderect(target.rect):
                target.kill();
                self.kill();
                player.xp += 10;

    def move(self, target):
        """ move along the vector between the origin point (player) and the mouse """
        if target.moving:
            x = 0;#target.speed;
        else:
            x = 0;

        dx = self.end[0] - self.rect.x;
        dy = self.end[1] - self.rect.y;
        distance = math.hypot(dx, dy);
        
        if distance:
            x_vel = (dx / distance) * (15 + x);
            y_vel = (dy / distance) * (15 + x); 
            self.rect.x += x_vel;
            self.rect.y += y_vel;

    def update(self, targets, player):
        self.move(player);
        self.collide(targets, player);
