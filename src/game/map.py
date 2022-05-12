import pygame

class Map:
    def __init__(self, screen, x, y, w, h, l=30):
        self.obj = pygame.Surface((w, h))
        self.obj.fill((180, 180, 180))
        self.rect = self.obj.get_rect(top=y, left=x)
        self.l = l
        self.blocks = []
        self.mapSpriteGroup = pygame.sprite.Group()
        self.screen = screen
        self._createBlockGrid(w, h, l)

    def _createBlockGrid(self, w, h, l):
        for block_x in range(0, w, l):
            for block_y in range(0, h, l):
                self.blocks.append(Block("floor", block_x, block_y, l))
                self.mapSpriteGroup.add(self.blocks[-1])

    def draw(self):
        # self.obj.fill((self.screen., 0, 0))
        self.screen.blit(self.obj, self.rect)
        for sprite in self.mapSpriteGroup:
            self.obj.blits([
                (sprite.obj, sprite.rect),
                (sprite.fg, sprite.fgr)
            ])

    def getClickedBlock(self, mouse_pos):
        for block in self.blocks:
            if block.checkClick(self._getRelativeCoordinates(mouse_pos)):
                return block
        return None

    def getCollidingBlocks(self, rect):
        colliding_blocks = []
        for block in self.blocks:
            if block.checkCollision(rect):
                colliding_blocks.append(block)
        return colliding_blocks

    def getRelativeRect(self):
        rr = self.rect.copy()
        rr.left, rr.top = 0, 0
        return rr

    def createSaveData(self):
        save_data = []
        for block in self.blocks:
            save_data.append(block.createSaveData())
        return save_data

    def loadSaveData(self, save_data):
        for block in enumerate(self.blocks):
            block[1].loadSaveData(save_data[block[0]])

    def clear(self):
        for block in self.blocks:
            block.type = "floor"
            block.selectSpriteByType()

    def _getRelativeCoordinates(self, pos):
        return pos[0] - self.rect.left, pos[1] - self.rect.top
        





class Block(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y, block_l):
        super().__init__()
        self.map = map
        self.obj = pygame.Surface((block_l, block_l))
        self.obj.fill((180, 180, 180))
        self.rect = self.obj.get_rect(top=pos_y, left=pos_x)
        self.fg = pygame.Surface((block_l-2, block_l-2))
        self.fgr = self.fg.get_rect(top=pos_y+1, left=pos_x+1)
        self.type = type
        self.typelist = {
            "floor": ((160, 160, 160), False),
            "wall": ((10, 10, 10), True),
            "finish": ((90, 255, 90), False),
        }
        self.selectSpriteByType()
        self.solid = False

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def checkCollision(self, other):
        if not self.solid:
            return False
        if self.rect.colliderect(other):
            return True
        else:
            return False

    def selectSpriteByType(self):
        self.fg.fill(self.typelist[self.type][0])
        self.solid = self.typelist[self.type][1]

    def changeBlockType(self):
        idx = list(self.typelist.keys()).index(self.type)
        self.type = list(self.typelist.keys())[(idx+1)%len(self.typelist)]
        print(self.type)
        self.selectSpriteByType()

    def createSaveData(self):
        return self.type

    def loadSaveData(self, data):
        self.type = data
        self.selectSpriteByType()