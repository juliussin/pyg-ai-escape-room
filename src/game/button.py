import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text, func):
        super().__init__()
        self.obj = pygame.Surface((w, h))
        self.obj.fill((50, 50, 50))
        self.rect = self.obj.get_rect(top=y, left=x)
        self.text = text
        self.func = func
        self.renderText()


    def renderText(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(self.text, True, (255, 255, 255))
        rect = text.get_rect(center=(self.rect.width/2, self.rect.height/2))
        self.obj.blit(text, rect)


    def draw(self, screen):
        screen.blit(self.obj, self.rect)


    def getClick(self, pos):
        if self.rect.collidepoint(pos):
            self.func()