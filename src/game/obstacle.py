import pygame

from .map import Map
from .object import DynamicObject



class BounceObstacle(DynamicObject):
    def __init__(self, map: Map, x, y, l, cvel=3, cdir=0):
        super().__init__(map, x, y, l, cvel)
        self.obj.fill((200, 50, 50))
        self.cdir = cdir
        self.dragdrop = False


    def stop(self):
        self.vel[self.cdir] = 0
    

    def play(self):
        self.vel[self.cdir] = self.cvel


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
                    self.vel[0] = self.cvel
                elif u[0] == 1:
                    self.vel[0] = -self.cvel
                elif u[0] == 2:
                    self.vel[1] = self.cvel
                elif u[0] == 3:
                    self.vel[1] = -self.cvel


    def onRMousePressed(self, pos):
        rpos = self.getRelativePos(pos)
        print(self.rect.center, rpos)
        if self.rect.collidepoint(rpos):
            self.dragdrop = True


    def onRMouseReleased(self):
        self.dragdrop = False


    def update(self):
        rpos = self.getRelativePos(pygame.mouse.get_pos())
        if self.dragdrop:
            self.rect.center = rpos
            return
        super().update()

    
    def createSaveData(self):
        sd = super().createSaveData() + (self.cdir,)
        return ("BounceObstacle", sd)



class RotatingObstacle(pygame.sprite.Sprite):
    def __init__(self, map: Map, x, y, l, cvel=3, cdir=0):
        super().__init__()
        self.map = map

        self.or_obj = pygame.Surface((150, 150))
        self.or_obj.fill((0,0,0))
        self.or_obj.set_colorkey((0,0,0))
        self.obj = self.or_obj.copy()
        self.or_rect = self.obj.get_rect(center=(x,y))
        self.rect = self.obj.get_rect(center=(x,y))
        
        self.cvel = cvel
        self.vel = 0
        self.cdir = cdir
        self.dragdrop = False
        self.curdeg = 0
        self.createBlade(l)


    def createBlade(self,l):
        print("createBlade")
        self.blades = []
        self.brect = []
        for i in range(8):
            self.blades.append(pygame.Surface((l, l)))
            self.blades[i].fill((150, 30, 30))
        self.brect.append(self.blades[0].get_rect(center=(self.rect.width/2+25, self.rect.height/2)))
        self.brect.append(self.blades[1].get_rect(center=(self.rect.width/2+65, self.rect.height/2)))
        # self.brect.append(self.blades[2].get_rect(center=(self.rect.width/2+105, self.rect.height/2)))
        self.brect.append(self.blades[2].get_rect(center=(self.rect.width/2-25, self.rect.height/2)))
        self.brect.append(self.blades[3].get_rect(center=(self.rect.width/2-65, self.rect.height/2)))
        # self.brect.append(self.blades[5].get_rect(center=(self.rect.width/2-105, self.rect.height/2)))
        self.brect.append(self.blades[4].get_rect(center=(self.rect.width/2, self.rect.height/2+25)))
        self.brect.append(self.blades[5].get_rect(center=(self.rect.width/2, self.rect.height/2+65)))
        # self.brect.append(self.blades[8].get_rect(center=(self.rect.width/2, self.rect.height/2+105)))
        self.brect.append(self.blades[6].get_rect(center=(self.rect.width/2, self.rect.height/2-25)))
        self.brect.append(self.blades[7].get_rect(center=(self.rect.width/2, self.rect.height/2-65)))
        # self.brect.append(self.blades[11].get_rect(center=(self.rect.width/2, self.rect.height/2-105)))
        self.or_obj.blits(zip(self.blades, self.brect))
            

    def draw(self):
        self.map.obj.blit(self.obj, self.rect)
        # pass


    def stop(self):
        self.vel = 0
    

    def play(self):
        self.vel = self.cvel * self.cdir


    def onRMousePressed(self, pos):
        rpos = self.getRelativePos(pos)
        print(self.rect.center, rpos)
        if self.rect.collidepoint(rpos):
            self.dragdrop = True


    def onRMouseReleased(self):
        self.dragdrop = False

    
    def getRelativePos(self, pos):
        rr = pos[0] - self.map.rect.left, pos[1] - self.map.rect.top
        return rr


    def update(self):
        rpos = self.getRelativePos(pygame.mouse.get_pos())
        if self.dragdrop:
            self.rect.center = rpos
            self.or_rect.center = rpos
            return
        self.drawRotate()
        

    def createSaveData(self):
        sd = (self.rect.x, self.rect.y, self.rect.width, self.cvel, self.cdir,)
        return ("RotatingObstacle", sd)


    def loadSaveData(self, data):
        self.rect.x = data[0]
        self.rect.y = data[1]
        self.rect.width = data[2]
        self.rect.height = data[2]
        self.cvel = data[3]


    def drawRotate(self):
        self.curdeg += self.vel
        """rotate an image while keeping its center and size"""
        self.obj = pygame.transform.rotate(self.or_obj, self.curdeg % 360)
        self.rect = self.obj.get_rect(center=self.or_rect.center)
