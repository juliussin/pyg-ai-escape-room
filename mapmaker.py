import os
import pickle

import easygui
import pygame

from src.game.button import Button
from src.game.map import Map
from src.game.obstacle import BounceObstacle, RotatingObstacle
from src.game.player import Player

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



class Level:
    def __init__(self, screen):
        self.screen = screen
        self.maps = Map(self.screen, 10, 110, 780, 480)
        self.player = Player(self.maps, 30, 100, 20)
        self.obstacles = pygame.sprite.Group()


    def save(self):
        save_map = self.maps.createSaveData()
        save_player = self.player.createSaveData()
        save_obstacles = []
        for obstacle in self.obstacles:
            save_obstacles.append(obstacle.createSaveData())
        filepath = easygui.filesavebox(default="levelX-Y.map", filetypes=["map"])
        if filepath is not None:
            with open(filepath, "wb") as f:
                pickle.dump((save_map, save_player, save_obstacles), f)

    
    def load(self):
        filepath = easygui.fileopenbox(default="levelX-Y.map", filetypes=["map"])
        if filepath is not None:
            with open(filepath, "rb") as f:
                data = f.read()
                smap, splayer, sobs = pickle.loads(data)
                self.maps.loadSaveData(smap)
                self.player.loadSaveData(splayer)
                self.obstacles.empty()
                print(sobs)
                for obs in sobs:
                    if obs[0] == 'BounceObstacle':
                        self.obstacles.add(BounceObstacle(self.maps, *obs[1]))



def main():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    FPS = 60
    CLOCK = pygame.time.Clock()

    level = Level(SCREEN)

    def addBounce(dir):
        print("add bounce")
        level.obstacles.add(BounceObstacle(level.maps, level.player.rect.centerx, level.player.rect.centery, 20, cvel=3, cdir=dir))
    def addRotating(dir):
        print("add rotating")
        level.obstacles.add(RotatingObstacle(level.maps, level.player.rect.centerx, level.player.rect.centery, 20, cvel=3, cdir=dir))
    def clearObstacle():
        print("remove obstacle")
        level.obstacles.empty()
    def playObstacle():
        print("play obstacle")
        for obstacle in level.obstacles:
            obstacle.play()
    def stopObstacle():
        print("stop obstacle")
        for obstacle in level.obstacles:
            obstacle.stop()
    def clearMap():
        print("clear map")
        level.maps.clear()

    buttons = pygame.sprite.Group()
    buttons.add(Button(10, 10, 150, 40, "Save Level", lambda: level.save()))
    buttons.add(Button(10, 60, 150, 40, "Load Level", lambda: level.load()))
    buttons.add(Button(180, 10, 150, 40, "Clear Obs", lambda: clearObstacle()))
    buttons.add(Button(180, 60, 150, 40, "Clear Map", lambda: clearMap()))
    buttons.add(Button(350, 10, 80, 40, "Play", lambda: playObstacle()))
    buttons.add(Button(350, 60, 80, 40, "Stop", lambda: stopObstacle()))
    buttons.add(Button(450, 10, 150, 40, "Add V-Obs", lambda: addBounce(dir=1)))
    buttons.add(Button(450, 60, 150, 40, "Add H-Obs", lambda: addBounce(dir=0)))
    buttons.add(Button(620, 10, 150, 40, "Add CW-Obs", lambda: addRotating(dir=1)))
    buttons.add(Button(620, 60, 150, 40, "Add CCW-Obs", lambda: addRotating(dir=-1)))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    block = level.maps.getClickedBlock(mouse_pos)
                    if block is not None:
                        block.changeBlockType()
                    for button in buttons:
                        button.getClick(mouse_pos)

                if event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for obstacle in level.obstacles:
                        obstacle.onRMousePressed(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for obstacle in level.obstacles:
                        obstacle.onRMouseReleased()

            if event.type == pygame.KEYDOWN:
                level.player.move(event.key)

            if event.type == pygame.KEYUP:
                level.player.stop(event.key)

        SCREEN.fill((180, 180, 180))
        level.maps.draw()
        level.player.update()
        level.player.draw()

        SCREEN.blits([(b.obj, b.rect) for b in buttons])

        for obstacle in level.obstacles:
            obstacle.update()
            obstacle.draw()

        pygame.display.update()
        CLOCK.tick(FPS)



if __name__ == '__main__':
    main()
