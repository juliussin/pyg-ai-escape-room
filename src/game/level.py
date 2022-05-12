import pickle

import easygui
import pygame

from src.game.map import Map
from src.game.obstacle import BounceObstacle, RotatingObstacle
from src.game.player import Player

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
        self.bgLoad(filepath)
        
    
    def bgLoad(self, filepath):
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
                    elif obs[0] == 'RotatingObstacle':
                        self.obstacles.add(RotatingObstacle(self.maps, *obs[1]))