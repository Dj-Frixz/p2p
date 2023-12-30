from sys import exit
from time import sleep
import pygame
from nsp2p import Graph

class GraphGui:

    def __init__(self, v, l) -> None:
        pygame.init()
        pygame.display.set_caption("nsp2p demonstration")
        self.screen = pygame.display.set_mode((800, 600))
        self.center = pygame.math.Vector2((400, 300))
        self.graph = Graph(v, l)
        self.elements = {}
        self.bg = self._nodes_surface()
        self.clean = 1
        self.FONT = pygame.font.SysFont('monospace', 20)
        self.delay = 0.1
        self.pause = False
        self.show_edges = True
        # pygame.display.set_icon( load_sprite("icon.ico", False))
    
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
                        self.graph.evolve()
                        self.clean = 1
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

    def _process_logic(self):
        self.path = self.graph.random_bfs(max_depth=256)

    def _draw(self):
        # if self.clean == 1:
        self.screen.fill((0,0,0))
        self.screen.blit(self.bg, (0,0))
        
        if self.show_edges:
            self._draw_edges(self.graph.edges)
        
        # self.clean = 0

        if self.path is not None:
            self._draw_node(self.elements[self.path[0]], (0,0,255))
            self._draw_node(self.elements[self.path[-1]], (255,0,0))
            self._draw_edges(zip(self.path[:-1], self.path[1:]), (0,255,0), 2)
        
        self.screen.blit(self.FONT.render('avg dist: '+str(self.graph.avg_distance), False, (255,255,255)), (600,50))
        self.screen.blit(self.FONT.render('tests: '+str(self.graph.tests), False, (255,255,255)), (600,80))
        self.screen.blit(self.FONT.render('delay: {:.1f}'.format(self.delay), False, (255,255,255)), (20,50))
        
        pygame.display.flip()

    def _nodes_surface(self):
        cursor = pygame.math.Vector2((-260, 0))
        angle = 360/len(self.graph.elements)

        for node in self.graph.elements:
            self.elements[node] = self.center + cursor
            self._draw_node(self.elements[node])
            cursor = cursor.rotate(angle)
        
        return self.screen.copy()
    
    def _draw_node(self, pos, color = (255, 255, 255)):
        pygame.draw.circle(self.screen, color, pos, 2)
    
    def _draw_edges(self, edges, color = (255,255,255), width = 1):
        for edge in edges:
            self._draw_edge(edge[0], edge[1], color, width)
    
    def _draw_edge(self, start_node, end_node, color = (255,255,255), width = 1):
        pygame.draw.line(self.screen, color, self.elements[start_node], self.elements[end_node], width)

if __name__ == '__main__':
    g = GraphGui(40, 5)
    g.main_loop()