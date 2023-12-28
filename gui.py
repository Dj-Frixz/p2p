from sys import exit
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

    def _process_logic(self):
        pass

    def _draw(self):
        self.screen.blit(self.bg, (0,0))
        self._draw_edges()
        pygame.display.flip()

    def _nodes_surface(self):
        cursor = pygame.math.Vector2((-260, 0))
        angle = 360/len(self.graph.elements)

        for node in self.graph.elements:
            self.elements[node] = self.center + cursor
            pygame.draw.circle(self.screen, (255,255,255), self.elements[node], 1)
            cursor = cursor.rotate(angle)
        
        return self.screen
    
    def _draw_edges(self):
        for edge in self.graph.edges:
            pygame.draw.line(self.screen, (255,255,255), self.elements[edge[0]], self.elements[edge[1]])

if __name__ == '__main__':
    g = GraphGui(20, 2)
    g.main_loop()