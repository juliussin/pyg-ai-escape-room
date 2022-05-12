import pygame
from .map import Map
from .object import DynamicObject

class Player(DynamicObject):
    def __init__(self, map: Map, x, y, l, cvel=3):
        super().__init__(map, x, y, l, cvel)
        self.obj.fill((50, 50, 250))
        

    def move(self, key):
        if key == pygame.K_UP:
            self.vel[1] = -self.cvel
        elif key == pygame.K_DOWN:
            self.vel[1] = self.cvel
        elif key == pygame.K_LEFT:
            self.vel[0] = -self.cvel
        elif key == pygame.K_RIGHT:
            self.vel[0] = self.cvel
        if self.vel[0] != 0 and self.vel[1] != 0:
            self.vel[0] = self.vel[0] * 0.707
            self.vel[1] = self.vel[1] * 0.707

    def stop(self, key):
        if key == pygame.K_UP:
            self.vel[1] = 0
            self.vel[0] = round(self.vel[0]/0.707)
        elif key == pygame.K_DOWN:
            self.vel[1] = 0
            self.vel[0] = round(self.vel[0]/0.707)
        elif key == pygame.K_LEFT:
            self.vel[0] = 0
            self.vel[1] = round(self.vel[1]/0.707)
        elif key == pygame.K_RIGHT:
            self.vel[0] = 0
            self.vel[1] = round(self.vel[1]/0.707)


    def collisionHandle(self, colliding_objects):
        if colliding_objects.__len__() > 0:
            for block in colliding_objects:
                # check distance of collision
                lOverlap = block.rect.right - self.rect.left
                rOverlap = self.rect.right - block.rect.left
                tOverlap = block.rect.bottom - self.rect.top
                bOverlap = self.rect.bottom - block.rect.top

                # sort based on distance
                overlapSolve = [lOverlap, rOverlap, tOverlap, bOverlap]
                u = sorted(range(len(overlapSolve)), key=lambda k: overlapSolve[k])
                
                # solve collision
                if u[0] == 0:
                    self.rect.left = block.rect.right
                elif u[0] == 1:
                    self.rect.right = block.rect.left
                elif u[0] == 2:
                    self.rect.top = block.rect.bottom
                elif u[0] == 3:
                    self.rect.bottom = block.rect.top