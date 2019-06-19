import pygame, math, sys;
from Button import Button;
from Control import Camera;
from Game import Player, Enemy, Item, Scenery, Wall;


WIN_WIDTH = 800;
WIN_HEIGHT = 600;


class Environment():

    """ The main class that controls the entire game """

    def __init__(self):
        self.entities = pygame.sprite.Group();
        self.walls = pygame.sprite.Group();
        self.enemies = pygame.sprite.Group();
        
        self.clock = pygame.time.Clock();
        self.fps = 30;
        self.running = False;

    def load_images(self):
        """ loads all the image files """
        # dont forget to convert them when you load them
        self.player_image = pygame.image.load("IMAGES\\player.png").convert_alpha();
        self.bush_image = pygame.image.load("IMAGES\\bush.png").convert_alpha();
        self.cursor_image = pygame.image.load("IMAGES\\cursor.png").convert_alpha();
        self.wall_image = pygame.image.load("IMAGES\\wall.png").convert_alpha();
        self.gem_image = pygame.image.load("IMAGES\\gem.png").convert_alpha();
        self.enemy_image = pygame.image.load("IMAGES\\banenemy.png").convert_alpha();
        self.bullet_image = pygame.image.load("IMAGES\\bullet.png").convert_alpha();
        self.gun_image = pygame.image.load("IMAGES\\gun.png").convert_alpha();
        self.exit_image = pygame.image.load("IMAGES\\door.png").convert();
        self.background_image = self.stitch(pygame.transform.scale(pygame.image.load("IMAGES\\background1.png").convert(), (32, 32)),
                                            self.level_width, self.level_height);
        self.water_image = pygame.Surface((32, 32));
        self.water_image.fill((0, 64, 255));

    def load_scene(self, file, clear=True):
        """ reads a text file with a level in it """
        if clear:
            self.entities.empty();
            self.walls.empty();
            self.enemies.empty();
        x, y = 0, 0;
        with open(file) as f:
            for row in f:
                for col in row:
                    if col in "1H":
                        Wall([self.entities, self.walls], (x, y), self.wall_image);
                    elif col in "2V":
                        Wall([self.entities, self.walls], (x, y), self.wall_image, "vertical");
                    elif col in "3B":
                        Scenery([self.entities], (x, y), self.bush_image);
                    elif col in "4W":
                        Scenery([self.entities], (x, y), self.water_image);
                    elif col in "5G":
                        Item([self.entities], (x, y), self.gem_image, self.player.increase_gems);
                    elif col in "6E":
                        Enemy([self.enemies], (x, y), self.enemy_image);
                    elif col in "7D":
                        Item([self.entities], (x, y), self.exit_image, self.end_game, False);
                    elif col in "8S":
                        Item([self.entities], (x, y), self.gun_image, self.player.activate_weapon)
                    x += 32;
                y += 32;
                x = 0;

    def get_scene_dimensions(self, file):
        with open(file) as f:
            lines = f.readlines();
            width = 32 * (len(lines[0]) - 1); # - 1 because of newline character
            height = 32 * len(lines);
            del lines;
        return width, height

    def stitch(self, image, total_width, total_height):
        """ Repeats an image so it fills the whole screen """
        total_width = max(800, total_width);
        total_height = max(600, total_height);
        x, y = 0, 0;
        *_, iwidth, iheight = image.get_rect();
        x_num = math.ceil(total_width / iwidth);
        y_num = math.ceil(total_height / iheight);
        background = pygame.Surface((total_width, total_height), pygame.SRCALPHA, 32);

        for i in range(y_num):
            for i2 in range(x_num):
                background.blit(image, (x, y));
                x += iwidth;
            y += iheight;
            x = 0;

        return background;

    def end_game(self, b=True, error=None):
        """ ends the game, exits the program, prints the results """
        pygame.quit();
        self.running = False;
        if b: print("Player XP: {}\nPlayer Level: {}\nPlayer Gems: {}".format(self.player.xp, self.player.level, self.player.gems));
        if error: raise error;
        sys.exit();

    def run(self, scene, title="game"):
        """ runs the game! """
        pygame.init();
        self.running = True;

        self.level_width, self.level_height = self.get_scene_dimensions(scene);
        self.window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT));
        self.camera = Camera(self.level_width, self.level_height, WIN_WIDTH, WIN_HEIGHT);
        pygame.display.set_caption(title);
        pygame.key.set_repeat(100, 50);

        pygame.mouse.set_visible(False);
        self.load_images();
        
        self.player = Player([], (100, 100), self.player_image);
        self.load_scene(scene);

        try:

            while self.running:

                mouse_pos = pygame.mouse.get_pos();

                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        self.running = False;
                        break;

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False;
                            break;
                        elif event.key == pygame.K_UP:
                            self.player.moving = True;
                        elif event.key == pygame.K_SPACE:
                            self.player.shooting = True

                    elif event.type == pygame.KEYUP:
                        if event.key == pygame.K_UP:
                            self.player.moving = False
                        elif event.key == pygame.K_SPACE:
                            self.player.shooting = False;

                self.player.update(self.walls, self.camera.reverse(mouse_pos), self.enemies);
                self.enemies.update(self.walls, self.player);
                self.entities.update(self.player);
                self.camera.update(self.player);
                
                self.player.shoot(self.camera.reverse(mouse_pos), self.bullet_image);

                self.window.blit(self.background_image, self.camera.apply_pos((0, 0)));
                for spr in self.entities:
                    self.window.blit(spr.image, self.camera.apply(spr));
                for en in self.enemies:
                    self.window.blit(en.image, self.camera.apply(en));
                for bul in self.player.bullets:
                    self.window.blit(bul.image, self.camera.apply(bul));
                self.window.blit(self.player.image, self.camera.apply(self.player));

                self.window.blit(self.cursor_image, (mouse_pos[0]-5, mouse_pos[1]-5));
                pygame.display.flip();

                self.clock.tick(self.fps);

        except Exception as e:
            # this is to make sure the pygame window closes if there is an error
            # because otherwise the window stops responding and it's hard to close
            self.end_game(error=e);

        self.end_game();


if __name__ == "__main__":
    env = Environment();
    env.run("scenes/scene3.txt");
