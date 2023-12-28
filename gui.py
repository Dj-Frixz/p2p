from sys import exit
from keyboard import is_pressed
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
        self.FONT = pygame.font.SysFont('monospace',int(20*(self.screen_height/1080)))
        # pygame.display.set_icon( load_sprite("icon.ico", False))
    
    def main_loop(self):
        while True:
            self._handle_input()
            self._process_logic()
            self._draw()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.graph.evolve()
                self.clean = 1

    def _process_logic(self):
        path = self.graph.random_bfs()

        if path is not None:
            self._draw_node(self.elements[path[0]], (0,0,255))
            self._draw_node(self.elements[path[-1]], (255,0,0))
            self._draw_edges(zip(path[:-1], path[1:]), (0,255,0))

    def _draw(self):
        if self.clean == 1:
            self.screen.fill((0,0,0))
            self.screen.blit(self.bg, (0,0))
            self._draw_edges(self.graph.edges)
            self.clean = 0
        
        pygame.display.flip()

    def _nodes_surface(self):
        cursor = pygame.math.Vector2((-260, 0))
        angle = 360/len(self.graph.elements)

        for node in self.graph.elements:
            self.elements[node] = self.center + cursor
            self._draw_node(self.elements[node])
            cursor = cursor.rotate(angle)
        
        return self.screen
    
    def _draw_node(self, pos, color = (255, 255, 255)):
        pygame.draw.circle(self.screen, color, pos, 3)
    
    def _draw_edges(self, edges, color = (255,255,255)):
        for edge in edges:
            self._draw_edge(edge[0], edge[1], color)
    
    def _draw_edge(self, start_node, end_node, color = (255,255,255)):
        pygame.draw.line(self.screen, color, self.elements[start_node], self.elements[end_node])

if __name__ == '__main__':
    g = GraphGui(256, 10)
    g.main_loop()