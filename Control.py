import pygame;


class Camera():

    """ scrolling camera so the world can be bigger than the screen """

    def __init__(self, total_width, total_height, viewport_width, viewport_height):
        self.state = pygame.Rect(0, 0, total_width, total_height);
        self.t_width, self.t_height = total_width, total_height;
        self.width, self.height = viewport_width, viewport_height;
        self.half_width, self.half_height = self.width // 2, self.height // 2;

    def new_state(self, rect):
        """ position the camera around the player """
        left, top, _, _ = rect;
        _, _, width, height = self.state;
        left, top, = self.half_width - left, self.half_height - top;

        left = min(0, max(self.width - self.state.width, left));
        top = min(0, max(self.height - self.state.height, top));

        return pygame.Rect(left, top, width, height);

    def apply(self, target):
        """ keep the player on screen """
        return target.rect.move(self.state.topleft);

    def apply_pos(self, pos):
        """ World Coors -> Screen Coors """
        return (pos[0] + self.state.left, pos[1] + self.state.top);

    def reverse(self, pos):
        """ Screen Coors -> World Coors """
        return (pos[0] - self.state.left, pos[1] - self.state.top);

    def update(self, target):
        if target == None:
            return;
        self.state = self.new_state(target.rect);
