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
                self.blocks.append(MapBlock("floor", block_x, block_y, l))
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

    def _getRelativeCoordinates(self, pos):
        return pos[0] - self.rect.left, pos[1] - self.rect.top
        





class MapBlock(pygame.sprite.Sprite):
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

        
    def collisionHandle(self, colliding_objects):
        pass


    def getRelativePos(self, pos):
        rr = pos[0] - self.map.rect.left, pos[1] - self.map.rect.top
        return rr



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
                    # self.rect.left = block.rect.right
                    self.vel[0] = -self.vel[0]
                elif u[0] == 1:
                    # self.rect.right = block.rect.left
                    self.vel[0] = -self.vel[0]
                elif u[0] == 2:
                    # self.rect.top = block.rect.bottom
                    self.vel[1] = -self.vel[1]
                elif u[0] == 3:
                    # self.rect.bottom = block.rect.top
                    self.vel[1] = -self.vel[1]


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



def main():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    FPS = 60
    CLOCK = pygame.time.Clock()

    maps = Map(SCREEN, 10, 110, 780, 480)
    player = Player(maps, 30, 100, 20)

    obstacles = pygame.sprite.Group()
    def addObstacle(dir):
        print("add obstacle")
        obstacles.add(BounceObstacle(maps, player.rect.centerx, player.rect.centery, 20, cvel=3, cdir=dir))
    def clearObstacle():
        print("remove obstacle")
        obstacles.empty()
    def playObstacle():
        print("play obstacle")
        for obstacle in obstacles:
            obstacle.play()
    def stopObstacle():
        print("stop obstacle")
        for obstacle in obstacles:
            obstacle.stop()

    buttons = pygame.sprite.Group()
    buttons.add(Button(10, 10, 150, 40, "Save Level", lambda: saveLevel(maps, player)))
    buttons.add(Button(10, 60, 150, 40, "Load Level", lambda: loadLevel(maps, player)))
    buttons.add(Button(180, 10, 150, 40, "Add V-Obs", lambda: addObstacle(dir=1)))
    buttons.add(Button(180, 60, 150, 40, "Add H-Obs", lambda: addObstacle(dir=0)))
    buttons.add(Button(350, 10, 150, 40, "Play", lambda: playObstacle()))
    buttons.add(Button(350, 60, 150, 40, "Stop", lambda: stopObstacle()))
    buttons.add(Button(520, 10, 150, 40, "Clear Obs", lambda: clearObstacle()))


    # bouncy1 = BounceObstacle(maps, 100, 100, 20, cdir=1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    block = maps.getClickedBlock(mouse_pos)
                    if block is not None:
                        block.changeBlockType()
                    for button in buttons:
                        button.getClick(mouse_pos)

                if event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for obstacle in obstacles:
                        obstacle.onRMousePressed(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for obstacle in obstacles:
                        obstacle.onRMouseReleased()

            if event.type == pygame.KEYDOWN:
                player.move(event.key)

            if event.type == pygame.KEYUP:
                player.stop(event.key)

        SCREEN.fill((180, 180, 180))
        maps.draw()
        player.update()
        player.draw()

        SCREEN.blits([(b.obj, b.rect) for b in buttons])

        for obstacle in obstacles:
            obstacle.update()
            obstacle.draw()

        pygame.display.update()
        CLOCK.tick(FPS)



if __name__ == '__main__':
    main()