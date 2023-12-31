import numpy as np

class Queue:
    def __init__(self) -> None:
        self.queue = []
    
    def __repr__(self) -> str:
        return 'Queue' + str(self.queue)
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def insert(self, __value):
        self.queue.append(__value)
    
    def read(self):
        return self.queue.pop(0)
    
    def reset(self):
        self.queue = []
    
    def copy(self):
        new_queue = Queue()
        new_queue.queue = self.queue.copy()
        return new_queue

class Node:
    def __init__(self, links: list[int] = []):
        self.links = links
        self.quality = []
        self.father = None
        self.candidates = []
    
    def __repr__(self) -> str:
        return str(self.links)
    
    def sort(self, reverse = True) -> None:
        links, quality = zip(*sorted(zip(self.links, self.quality), key=lambda x: x[1], reverse=reverse))
        self.links, self.quality = list(links), list(quality)
    
    def add_link(self, link, quality) -> None:
        self.links += [link]
        self.quality += [quality]

    def remove_link(self, link):
        if link in self.links:
            i = self.links.index(link)
            self.links.pop(i)
            self.quality.pop(i)

    def increment_quality(self, link, amount = 1):
        self.quality[self.links.index(link)] += 1
    
    def add(self, n_add):
        self.candidates.sort(key = lambda x: x[1], reverse = True)
        added = []
        for x in self.candidates:
            if x[0] not in self.links:
                added.append(x)
            if len(added)==n_add:
                break
        
        added_links, added_quality = zip(*added) if len(added)!=0 else ([], [])
        self.links, self.quality = self.links + list(added_links), self.quality + list(added_quality)
        return added
    
    def remove(self, l):
        self.sort()
        n_rem = len(self.links) - l

        if n_rem > 0:
            removed = self.links[-n_rem:]
            self.links = self.links[:-n_rem]
            self.quality = self.quality[:-n_rem]
            return removed
        
        return []

    def reset(self):
        self.candidates = []
        self.quality = [0] * len(self.quality)

class Graph:

    def __init__(self, v = 256, l = 10):
        self.elements = {}
        self.l = l
        self.avg_distance = 0
        self.tests = 0
        self.init_graph(v, l)
    
    def __repr__(self) -> str:
        return str(self.elements)
    
    def __str__(self) -> str:
        string = ''
        for id in self.elements:
            string += '  Node {} links->{} quality->{}\n'.format(id, self.elements[id].links, self.elements[id].quality)
        return string
    
    @property
    def vertices(self):
        return list(self.elements)
    
    @property
    def edges(self):
        e = set()
        for node in self.elements:
            for link in self.elements[node].links:
                e.add((min(node, link), max(node, link)))
        return e
    
    @property
    def unilinks(self):
        '''Used for debugging'''
        edges = []
        for node in self.elements:
            for link in self.elements[node].links:
                edges.append((node, link))
        edges.sort(key=lambda x: (min(x), max(x)))
        return edges

    def init_graph(self, v, l):
        ids = np.arange(v, dtype=np.uint8)
        values = np.random.choice(ids, size=v, replace=False)
        free_nodes = values.copy()
        for i in ids:
            node = values[i]
            pred_succ = [values[(i-1) % v], values[(i+1) % v]]
            free_nodes = np.delete(free_nodes, 0) if node in free_nodes else free_nodes
            choices = np.delete(free_nodes, 0) if pred_succ[1] in free_nodes else free_nodes
            if i==0:
                choices = np.delete(choices, v-3)   # remove if structure should not be circular
            
            if node not in self.elements:
                self.elements[node] = Node()
            
            links = list(np.random.choice(choices, min(l - len(self.elements[node].links), choices.size), replace=False))
            self.elements[node].links = pred_succ + self.elements[node].links + links

            for link in links:
                if link in self.elements:
                    self.elements[link].links += [node]
                else:
                    self.elements[link] = Node([node])

                if len(self.elements[link].links) == l:
                    free_nodes = np.delete(free_nodes, np.nonzero(free_nodes==link))
            
            self.elements[node].quality = [0] * len(self.elements[node].links)
    
    def bfs(self, start, searched, max_depth = 4):
        node = start
        depth = 0
        queue1 = Queue()
        queue2 = Queue()
        visited = {node}

        while (node!=searched and depth<=max_depth):

            for link in self.elements[node].links:
                if link not in visited:
                    queue2.insert(link)
                    self.elements[link].father = node
                    visited.add(link)
            
            if queue1.is_empty():
                if queue2.is_empty():
                    return
                queue1 = queue2.copy()
                queue2.reset()
                depth += 1

            node = queue1.read()
        
        if node != searched:
            return None
        
        return self.quality_update(node, start, depth)
    
    def quality_update(self, node, start, depth):
        path = [node]

        while node != start:
            father = self.elements[node].father
            self.elements[node].increment_quality(father, depth)
            self.elements[father].increment_quality(node, depth)
            node = father
            path.insert(0, node)
        
        self.avg_distance = (self.avg_distance * self.tests + depth) / (self.tests + 1)
        self.tests += 1
        
        return path

    def random_bfs(self, max_depth = 4):
        values = np.array(list(self.elements))
        start = np.random.choice(values)
        searched = np.random.choice(values[values!=start])
        return self.bfs(start, searched, max_depth)

    def simulate(self, iterations = 100, max_depth = 4):
        for _ in range(iterations):
            print('random path:',self.random_bfs(max_depth))
    
    def evolve(self, n_share = 3):
        # Share phase
        for node in self.elements:
            self.elements[node].sort()
            
            for link,quality in zip(self.elements[node].links, self.elements[node].quality):
                shared = list(zip(self.elements[node].links, self.elements[node].quality))
                shared.remove((link, quality))
                shared = shared[:n_share]
                nodes, quals = zip(*self.elements[link].candidates) if len(self.elements[link].candidates)!=0 else ([], [])
                for x in shared:
                    if x[0] in nodes:
                        i = nodes.index(x[0])
                        if x[1] > quals[i]:
                            self.elements[link].candidates[i] = x
                    else:
                        self.elements[link].candidates += [x]
        
        # Add phase
        for node in self.elements:
            added = self.elements[node].add(n_share)
            for link, quality in added:
                self.elements[link].add_link(node, quality)
        
        # Remove phase
        for node in self.elements:
            removed = self.elements[node].remove(self.l)
            for link in removed:
                self.elements[link].remove_link(node)
        
        # Reset phase
        for node in self.elements:
            self.elements[node].reset()
        
        self.avg_distance = 0
        self.tests = 0

    def draw(self, start, max_depth):
        string = ''
        queue1 = Queue()
        queue2 = Queue()
        queue1.insert(start)
        depth = 0
        while depth <= max_depth:
            while not queue1.is_empty():
                node = queue1.read()
                string += str(node) + ' '

                for link in self.elements[node].links:
                    queue2.insert(link)
            
            queue1 = queue2.copy()
            queue2.reset()
            depth += 1
            string += '\n'
        
        print(string)
        

if __name__ == '__main__':
    graph = Graph(20, 2)
    iterations = 1000
    graph.simulate(iterations)
    print(graph)
    graph.evolve()
    print(graph)