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
        self.quality = [0] * len(links)
        self.father = None
        self.candidates = []
    
    def __repr__(self) -> str:
        return str(self.links)
    
    def sort(self, reverse = True) -> None:
        links, quality = zip(*sorted(zip(self.links, self.quality), key=lambda x: x[1], reverse=reverse))
        self.links, self.quality = list(links), list(quality)

    def increment_quality(self, link, amount = 1):
        self.quality[self.links.index(link)] += amount

    def update(self, l, n = 3):
        self.candidates = sorted(self.candidates, reverse=True, key=lambda x: x[1])[:n]
        
        for i in range(len(self.candidates)):
            worst = min(self.quality)

            if worst < self.candidates[i][1]:
                j = self.quality.index(worst)
                self.links[j] = self.candidates[i][0]
                self.quality[j] = self.candidates[i][1]
            else:
                break
        
        self.sort()
        self.links = self.links[:l]
        self.reset()

    def reset(self):
        self.candidates = []
        self.quality = [0] * len(self.quality)

class Network:

    def __init__(self, v = 256, l = 8):
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

        return sorted(edges)

    def init_graph(self, v, l):
        ids = np.arange(v, dtype=np.uint8)
        values = np.random.choice(ids, size=v, replace=False)

        for i in ids:
            node = values[i]
            pred_succ = [values[(i-1) % v], values[(i+1) % v]]
            mask = (values!=node)*(values!=pred_succ[0])*(values!=pred_succ[1])
            links = np.random.choice(values[mask], l, replace=False)
            self.elements[node] = Node(pred_succ + list(links))
    
    def bfs(self, start, searched, max_depth = 4):
        node = start
        depth = 0
        queue1 = Queue()
        queue2 = Queue()
        visited = set()

        while (depth<=max_depth):

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
            if node == searched:
                break
        
        if node != searched:
            return None
        
        return self.quality_update(node, start, depth)
    
    def quality_update(self, node, start, depth):
        path = [node]
        node = self.elements[node].father

        while node != start:
            self.elements[node].increment_quality(path[0], 1)
            path.insert(0, node)
            node = self.elements[node].father
        
        path.insert(0, node)
        
        self.avg_distance = (self.avg_distance * self.tests + depth) / (self.tests + 1)
        self.tests += 1
        
        return path

    def random_bfs(self, max_depth = 4):
        values = np.array(list(self.elements))
        start = np.random.choice(values)
        searched = np.random.choice(values) # (values[values!=start])   !!
        return self.bfs(start, searched, max_depth)

    def simulate(self, iterations = 100, max_depth = 4, verbose = False):
        for _ in range(iterations):
            path = self.random_bfs(max_depth)

            if verbose == True:
                print('random path:',path)
    
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
        
        # Update phase
        for node in self.elements:
            self.elements[node].update(self.l + 2)  
        
        self.avg_distance = 0
        self.tests = 0
    
    def integrity_check(self, max_depth = 5):
        '''Every node search for itself in the network to find out 
        if they are still connected, otherwise force links with their neighbors.'''

        for node in self.elements:
            if self.bfs(node, node, max_depth) == None:
                for link in self.elements[node].links:
                    self.elements[link].links.append(node)
                    self.elements[link].quality.append(0)

    def draw(self, start, max_depth):
        '''Used for debugging purposes'''
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
    net = Network(20, 2)
    iterations = 1000
    net.simulate(iterations)
    print(net)
    net.evolve()
    print(net)