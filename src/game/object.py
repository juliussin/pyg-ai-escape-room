import pygame
from .map import Map



class DynamicObject(pygame.sprite.Sprite):
    def __init__(self, map: Map, x, y, l, cvel=3):
        super().__init__()
        self.map = map
        self.obj = pygame.Surface((l, l))
        self.rect = self.obj.get_rect(center=(x, y))
        self.cvel = cvel
        self.vel = [0, 0]

    def draw(self):
        self.map.obj.blit(self.obj, self.rect)

    
    def createSaveData(self):
        return (self.rect.x, self.rect.y, self.rect.width, self.cvel)


    def loadSaveData(self, data):
        self.rect.x = data[0]
        self.rect.y = data[1]
        self.rect.width = data[2]
        self.rect.height = data[2]
        self.cvel = data[3]

    
    def update(self):
        self.rect.move_ip(self.vel)
        self.rect.clamp_ip(self.map.getRelativeRect())
        collision = self.map.getCollidingBlocks(self.rect)
        self.collisionHandle(collision)


    def getRelativePos(self, pos):
        rr = pos[0] - self.map.rect.left, pos[1] - self.map.rect.top
        return rr


    def play(self):
        pass


    def stop(self):
        pass


    def collisionHandle(self, colliding_objects):
        pass
