import pygame;


class Button(pygame.sprite.Sprite):

    def __init__(self, groups=[], text="", width=None, height=None, acolor=(255, 255, 255),
                 icolor=(128, 128, 128), hcolor=(128, 0, 0), active=True, text_align="center", font_size=32,
                 font_color=(255, 0, 0), font="corbel", x_pos=0, y_pos=0, visible=True, onclick=lambda: None,
                 border_color=(0, 0, 0), border_width=2):
        pygame.sprite.Sprite.__init__(self);
        
        self.text = text;
        self.font = pygame.font.SysFont(font, font_size).render(text, 1, font_color);
        self.width, self.height = self.get_rect_size(width, height);
        self.image = pygame.Surface((self.width, self.height));
        self.rect = self.image.get_rect();
        self.rect.x = x_pos;
        self.rect.y = y_pos;
        
        self.active = active;
        self.visible = visible;
        self.acolor = acolor;
        self.icolor = icolor;
        self.hcolor = hcolor;
        self.border_width = border_width;
        self.border_color = border_color;

        if self.active:
            self.color = self.acolor;
        else:
            self.color = self.icolor;

        self.text_align = text_align;
        self.text_x, self.text_y = self.handle_text_align();
        self.onclick = onclick;

        self.add(*groups);

    def get_rect_size(self, w, h):
        if w == None:
            w = self.font.get_width() + 40;
        if h == None:
            h = self.font.get_height() + 20;
        return int(w), int(h);

    def handle_text_align(self):
        if self.text_align in ("center", "center-top", "center-bottom"):
            x = (self.width - self.font.get_width()) / 2;
        elif self.text_align in ("left", "left-top", "left-bottom"):
            x = 0;
        elif self.text_align in ("right", "right-top", "right-bottom"):
            x = self.width - self.font.get_width();
        else:
            x = 0;

        if self.text_align in ("center", "left", "right"):
            y = (self.height - self.font.get_height()) / 2;
        elif self.text_align in ("center-top", "left-top", "right-top"):
            y = 0;
        elif self.text_align in ("center-bottom, left-bottom, right-bottom"):
            y = self.height - self.font.get_height();
        else:
            y = 0;

        return x, y;

    def toggle_active(self):
        self.active = bool(self.active - 1);

    def toggle_visible(self):
        if self.visible:
            self.visible = False;
            self.active = False;
        else:
            self.visible = True;
            self.active = True;

    def get_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN) and (self.rect.collidepoint(pygame.mouse.get_pos()));

    def get_hover(self):
        return self.rect.collidepoint(pygame.mouse.get_pos());

    def display(self):
        self.image.fill(self.color);
        self.image.blit(self.font, (self.text_x, self.text_y));
        pygame.draw.rect(self.image, self.border_color,
                         (0, 0, self.width, self.height-self.border_width), self.border_width);

    def draw(self, surface):
        surface.blit(self.image, self.rect);

    def update(self, event):
        if self.active:
            if self.get_hover():
                self.color = self.hcolor;
            else:
                self.color = self.acolor;
            if self.get_clicked(event):
                return self.onclick();
        else:
            self.color = self.icolor;

        if self.visible:
            self.display();
