from sys import exit
from time import sleep
import pygame
from nsp2p import Network

class NetGui:

    def __init__(self, v, l) -> None:
        pygame.init()
        pygame.display.set_caption("NetSim")
        self.screen = pygame.display.set_mode((800, 600))
        # pygame.display.set_icon( load_sprite("icon.ico", False))
        self.center = pygame.math.Vector2((400, 300))
        self.net = Network(v, l)
        self.elements = {}
        self.bg = self._nodes_surface()
        self.bg_wedges = self._draw_edges(self.bg.copy(), self.net.edges)
        self.clean = 1
        self.FONT = pygame.font.SysFont('monospace', 20)
        self.delay = 0
        self.pause = False
        self.show_edges = True
        self.fast_mode = False
    
    def main_loop(self):
        while True:
            self._handle_input()
            if not self.pause: self._process_logic()
            self._draw()
            sleep(self.delay)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_RETURN:
                        self.evolve()
                    case pygame.K_UP:
                        self.delay += 0.1
                    case pygame.K_DOWN:
                        self.delay = self.delay - 0.1 if self.delay > 0.1 else 0
                    case pygame.K_SPACE:
                        self.pause = self.pause == False
                    case pygame.K_RIGHT:
                        self._process_logic()
                    case pygame.K_h:
                        self.show_edges = self.show_edges == False
                    case pygame.K_f:
                        self.fast_mode = self.fast_mode == False

    def _process_logic(self):
        if self.net.tests >= 1000:
            self.evolve()
        
        if self.fast_mode:
            self.net.simulate(1000)
        else:
            self.path = self.net.random_bfs(max_depth=4)

    def _draw(self):
        # if self.clean == 1:
        self.screen.fill((0,0,0))
        
        if self.show_edges:
            self.screen.blit(self.bg_wedges, (0,0))
        else:
            self.screen.blit(self.bg, (0,0))
        
        if not self.fast_mode and self.path is not None:
            self._draw_node(self.elements[self.path[0]], (0,0,255))
            self._draw_node(self.elements[self.path[-1]], (255,0,0))
            self._draw_edges(self.screen, zip(self.path[:-1], self.path[1:]), (0,255,0), 2)
        
        self.screen.blit(self.FONT.render('avg dist: '+str(self.net.avg_distance), False, (255,255,255)), (600,50))
        self.screen.blit(self.FONT.render('tests: '+str(self.net.tests), False, (255,255,255)), (600,80))
        self.screen.blit(self.FONT.render('delay: {:.1f}'.format(self.delay), False, (255,255,255)), (20,50))
        
        pygame.display.flip()

    def _nodes_surface(self):
        cursor = pygame.math.Vector2((-260, 0))
        angle = 360/len(self.net.elements)

        for node in self.net.elements:
            self.elements[node] = self.center + cursor
            self._draw_node(self.elements[node])
            cursor = cursor.rotate(angle)
        
        return self.screen.copy()
    
    def _draw_node(self, pos, color = (255, 255, 255)):
        pygame.draw.circle(self.screen, color, pos, 2)
    
    def _draw_edges(self, surface, edges, color = (255,255,255), width = 1):
        for edge in edges:
            pygame.draw.line(surface, color, self.elements[edge[0]], self.elements[edge[1]], width)
        
        return surface
    
    def evolve(self):
        self.net.evolve()
        self.net.integrity_check()
        self.bg_wedges = self._draw_edges(self.bg.copy(), self.net.edges)
