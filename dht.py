


class Node:
    
    def __init__(self, k, pred, succ, pred_distance) -> None:
        self.pred = pred
        self.pred_distance = pred_distance
        self.FT = [succ] * k
        self.cicle = 2**k
        self.resources = []
    
    def __repr__(self) -> str:
        return 'Node' + str(self.resources)

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id
    
    def __ne__(self, __value: object) -> bool:
        return self.id != __value.id
    
    @property
    def succ(self) -> int:
        return self.FT[0]
    
    @succ.setter
    def succ(self, id)  -> None:
        self.FT[0] = id


class Ring:

    def __init__(self, k) -> None:
        self.start_id = None
        self.k = k
        self.elements = {}
        self.__2_pow = [2**i for i in range(k+1)]
    
    def __repr__(self) -> str:
        return str(list(self.elements))

    def distance(self, start, stop):
        return (stop - start) % self.__2_pow[self.k]
    
    def is_not_in_node(self, __value, node):
        return self.distance(__value, node) >= self.elements[node].pred_distance

    def linear_search_on_ring(self, t_ids, id) -> int:
        if self.elements[id].pred_distance == 0:
            return id
        
        while self.is_not_in_node(t_ids, id):
            id = self.elements[id].succ
        return id

    def circular_search_on_ring(self, t_ids, start):
        node = start

        if self.elements[node].pred_distance == 0:
            return node

        i = self.k

        while self.is_not_in_node(t_ids, node):
            i = self._int_log2(self.distance(node, t_ids), i-1)
            if i==0:
                return self.elements[node].succ
            node = self.elements[node].FT[i]
        return node

    def linear_insert_on_ring(self, id):
        if self.start_id == None:
            self.elements[id] = Node(self.k, id, id, 0)
            self.start_id = id
        else:
            succ = self.linear_search_on_ring(id, self.start_id)
            self._insert_id_before_node(id, succ)

    def _insert_id_before_node(self, id, succ):
        pred = self.elements[succ].pred
        self.elements[id] = Node(self.k, pred, succ, self.distance(pred, id))
        self.elements[succ].pred = id
        self.elements[succ].pred_distance = self.distance(id, succ)
        self.elements[pred].succ = id

        self.start_id = id
    
    def circular_insert_on_ring(self, id):
        if self.start_id == None:
            self.elements[id] = Node(self.k, id, id, 0)
            self.start_id = id
        else:
            succ = self.circular_search_on_ring(id, self.start_id)
            self._insert_id_before_node(id, succ)
        self._fill_FT(id)
        
    def _fill_FT(self, id):
        '''Updates every row of a node's FT'''
        for i in range(1,self.k):
            self.elements[id].FT[i] = self.circular_search_on_ring(self.distance(0, id + self.__2_pow[i]), self.elements[id].FT[i-1])
        
        pred = self.elements[id].pred
        self._fix_pred_node_FT(id, pred)

        start = self.elements[pred].FT[self.k - 1]
        self._iteratively_fix_FTs(id, pred, start)
    
    def _fix_pred_node_FT(self, id, pred):
        distance = self.distance(pred, id)
        
        for i in range(1, self.k):
            if self.__2_pow[i] > distance:
                return
            self.elements[pred].FT[i] = id
        
    def _iteratively_fix_FTs(self, id, pred, start):
        '''Updates some nodes' FT after a node creation'''

        log_distance = self.k - 1

        while True:
            log_distance = self._int_log2(self.distance(start, id), log_distance)
            if log_distance == 0:
                return
            
            # the range of nodes to fix is (low, high]
            low = self.distance(0, pred - self.__2_pow[log_distance] + 1)
            high = self.distance(0, id - self.__2_pow[log_distance])
            start = self.circular_search_on_ring(low, start)
            node = start
            
            distance = self.distance(low, high)

            while self.distance(low, node) <= distance:
                self.elements[node].FT[log_distance] = id
                node = self.elements[node].succ
            
            log_distance -= 1
            start = self.elements[self.elements[start].pred].FT[log_distance]
    
    def _int_log2(self, distance, k):
        '''### return min(floor(log2(distance)), k) if log2(distance)>=0 else return 0'''
        for i in range(k, 0, -1):
            if distance >= self.__2_pow[i]:
                return i
        return 0
        

class DHT:

    def __init__(self, k) -> None:
        self.ring = Ring(k)
        self.n = 0
    
    def __str__(self) -> str:
        id = self.ring.start_id
        seen_ids = set()
        string = '\nDHT[k={}, range=[0-{}], n={}, start={}] (\n\n'.format(self.ring.k, 2**self.ring.k - 1, self.n, id)
        for _ in range(self.n):
            string += '+' if id in seen_ids else ''
            seen_ids.add(id)
            string += '\tNode[{}]{}\n'.format(id, self.ring.elements[id].FT)
            id = self.ring.elements[id].succ
        return string + '\n)\n'

    def is_empty(self):
        return self.n == 0

    def linear_search(self, t_ids):
        return self.ring.linear_search_on_ring(t_ids, self.ring.start_id)
    
    def linear_insert(self, id):
        self.ring.linear_insert_on_ring(id)
        self.n += 1
    
    def search(self, t_ids):
        return self.ring.circular_search_on_ring(t_ids, self.ring.start_id)
    
    def insert(self, id):
        self.ring.circular_insert_on_ring(id)
        self.n += 1




def test():
    from random import randint, shuffle
    k = 4
    n = 250
    ids = list({randint(0, 2**k - 1) for _ in range(n)})
    shuffle(ids)
    mem = DHT(k)
    for id in ids:
        mem.insert(id)
    print(mem)


if __name__=='__main__':
    test()