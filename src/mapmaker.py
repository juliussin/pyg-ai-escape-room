import os, pickle, easygui
import pygame


main_dir = os.path.split(os.path.abspath(__file__))[0]
sprite_dir = os.path.join(main_dir, 'sprite')



def loadImage(path, colorkey=None, scale=1):
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    image = image.convert()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    
    return image



def saveLevel(maps, player):
    smap = maps.createSaveData()
    splayer = player.createSaveData()
    filepath = easygui.filesavebox(default="data.map", filetypes=["map"])
    if filepath is not None:
        with open(filepath, "wb") as f:
            pickle.dump((smap, splayer), f)



def loadLevel(maps, player):
    filepath = easygui.fileopenbox(default="data.map", filetypes=["map"])
    if filepath is not None:
        with open(filepath, "rb") as f:
            data = f.read()
            smap, splayer = pickle.loads(data)
            maps.loadSaveData(smap)
            player.loadSaveData(splayer)



class Map:
    def __init__(self, x,y,w,h,l=28):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.l = l
        self.blocks = []
        self.mapSpriteGroup = pygame.sprite.Group()
        self._createBlockGrid()

    def _createBlockGrid(self):
        for block_x in range(self.x+1, self.x + self.w, self.l+2):
            for block_y in range(self.y+1, self.y + self.h, self.l+2):
                self.blocks.append(MapBlock("floor", block_x, block_y, self.l))
                self.mapSpriteGroup.add(self.blocks[-1])

    def draw(self, screen):
        for sprite in self.mapSpriteGroup:
            screen.blit(sprite.obj, sprite.rect)

    def getClickedBlock(self, mouse_pos):
        for block in self.blocks:
            if block.checkClick(mouse_pos):
                return block
        return None

    def getCollidingBlocks(self, rect):
        colliding_blocks = []
        for block in self.blocks:
            if block.checkCollision(rect):
                colliding_blocks.append(block)
        return colliding_blocks

    def createSaveData(self):
        save_data = []
        for block in self.blocks:
            save_data.append(block.createSaveData())
        return save_data

    def loadSaveData(self, save_data):
        for block in enumerate(self.blocks):
            block[1].loadSaveData(save_data[block[0]])
        





class MapBlock(pygame.sprite.Sprite):
    def __init__(self, type, pos_x, pos_y, block_l):
        super().__init__()
        self.obj = pygame.Surface((block_l, block_l))
        self.rect = self.obj.get_rect(top=pos_y, left=pos_x)
        self.type = type
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
        if self.type == "wall":
            self.obj.fill((10, 10, 10))
            self.solid = True
        elif self.type == "floor":
            self.obj.fill((160, 160, 160))
            self.solid = False

    def changeBlockType(self):
        if self.type == "wall":
            self.type = "floor"
        elif self.type == "floor":
            self.type = "wall"
        self.selectSpriteByType()

    def createSaveData(self):
        return self.type

    def loadSaveData(self, data):
        self.type = data
        self.selectSpriteByType()



class Player(pygame.sprite.Sprite):
    def __init__(self, map, x, y, l, cvel=3):
        super().__init__()
        self.map = map
        self.obj = pygame.Surface((l, l))
        self.obj.fill((50, 50, 250))
        self.rect = self.obj.get_rect(center=(x, y))
        self.vel = [0, 0]
        self.cvel = cvel

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

    def update(self):
        self.rect.move_ip(self.vel)
        if self.rect.left < self.map.x:
            self.rect.left = self.map.x
        elif self.rect.right > self.map.x + self.map.w:
            self.rect.right = self.map.x + self.map.w
        if self.rect.top < self.map.y:
            self.rect.top = self.map.y
        elif self.rect.bottom > self.map.y + self.map.h:
            self.rect.bottom = self.map.y + self.map.h
        collision = self.map.getCollidingBlocks(self.rect)
        if collision.__len__() > 0:
            for block in collision:
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


    def draw(self, screen):
        screen.blit(self.obj, self.rect)

    
    def createSaveData(self):
        return (self.rect.x, self.rect.y, self.rect.width, self.cvel)


    def loadSaveData(self, data):
        self.rect.x = data[0]
        self.rect.y = data[1]
        self.rect.width = data[2]
        self.rect.height = data[2]
        self.cvel = data[3]



def main():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    FPS = 60
    CLOCK = pygame.time.Clock()

    maps = Map(30, 100, 720, 450)
    player = Player(maps, 30, 100, 20)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                saveLevel(maps, player)
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    block = maps.getClickedBlock(pygame.mouse.get_pos())
                    if block is not None:
                        block.changeBlockType()

                if event.button == 3:
                    loadLevel(maps, player)

            if event.type == pygame.KEYDOWN:
                player.move(event.key)

            if event.type == pygame.KEYUP:
                player.stop(event.key)

        SCREEN.fill((180, 180, 180))
        maps.draw(SCREEN)
        player.update()
        player.draw(SCREEN)

        pygame.display.update()
        CLOCK.tick(FPS)



if __name__ == '__main__':
    main()