"""
A new implementation of Ukkonen's algorithm, slightly different from the one provided by the original paper.
"""


class Graph_with_edge_content:
    """
    A graph with edge content 'g' is a graph
    with vertices labeled from '0' to 'g.number_of_vertices() - 1'
    Each vertex has a set of edges, represented by a dictionary indexed by edge labels.
    Each edge has a content, which can be anything,
    but should (for the sake of semantic) include the vertex it points to.
    """
    #
    def __init__(self):
        self.root = 0
        self.__adjacencies__ = [{}]
    #
    def number_of_vertices(self):
        return len(self.__adjacencies__)
    # adds a new vertex to the graph and returns its label
    def add_new_vertex(self):
        self.__adjacencies__.append({})
        return self.number_of_vertices() - 1
    # tests if 'vertex' has an edge of label 'edge_label'
    def has_edge(self, vertex, edge_label):
        return edge_label in self.__adjacencies__[vertex]
    # returns the content of the edge of label 'edge_label' linked to 'vertex'
    def get_edge_content(self, vertex, edge_label):
        return self.__adjacencies__[vertex][edge_label]
    # change the content of an edge
    def update_edge_content(self, vertex, edge_label, edge_content):
        self.__adjacencies__[vertex][edge_label] = edge_content
    #
    def print(self):
        print(self.__adjacencies__)



class Implicit_state:
    """
    The paper of Ukkonen 'On-line construction of suffix trees', Algorithmica,
    defines the "suffix-tree" of a word, and the notion of "implicit state".

    Informally, the suffix-tree of the word 'word' is a rooted tree where
    - each edge wear a string,
    - each internal node (except possibly the root) has at least two children,
    - any factor of 'word' can be read starting from the root
      and reading the strings along the traversed edges.
    Furthermore, "suffix edges" are added to the tree
    (hence, the suffix-tree need not be an actual tree).

    To gain space, the content of an edge is not the string attached to it.
    It is a triplet '(pos, len, label)', where
    - 'label' is the label of the vertex the edge points to,
    - the string of the edge is 'word[pos, pos + len]'.
    The content of a suffix edge is just the label of the vertex it points to

    An "implicit state" 's' contains all the information of suffix-tree,
    as well as the values 'label', 'pos', and 'length'.    
    """
    #
    def __init__(self, word, leafs_length = 'word length'):
        self.word = word
        self.tree = Graph_with_edge_content()
        self.root = 0
        self.label = 0
        self.pos = 0
        self.len = 0
        if leafs_length == 'word length':
            self.leafs_length = len(self.word)
        elif leafs_length == 'infinity':
            import math
            self.leafs_length = math.inf
    #
    def print(self):
        print(self.label, self.pos, self.len)
        print(self.tree.__adjacencies__)
    #
    def is_explicit(self):
        return self.len == 0
    #
    def is_root(self):
        return (self.label == self.root and self.pos == 0 and self.len == 0)
    #
    def has_transition(self, position):
        # outputs the Boolean 'True' iff the canonical implicit state '(state, k, p)'
        # has a 'letter'-transition, and 'False' otherwise
        if self.is_explicit():
            # if '(k, p)' represents the empty word, then 'state' is an explicit state,
            # and we test if 'letter' is one of its transitions
            return self.tree.has_edge(self.label, self.word[position])
        k = self.tree.get_edge_content(self.label, self.word[self.pos])[0]
        return self.word[position] == self.word[k + self.len]
    #
    def move(self, label, pos, length):
        self.label = label
        self.pos = pos
        self.len = length
    #
    def make_canonical(self):
        if not self.is_explicit():
            p, l, s = self.tree.get_edge_content(self.label, self.word[self.pos])
            while l < self.len:
                self.move(s, self.pos + l, self.len - l)
                p, l, s = self.tree.get_edge_content(self.label, self.word[self.pos])
            if l == self.len:
                self.move(s, 0, 0)
    #
    def move_to_suffix(self):
        # 'self' is assumed not to be the root
        if self.label == self.root:
            self.len -= 1
            if self.len == 0:
                self.pos = 0
            else:
                self.pos += 1
        else:
            self.label = self.tree.get_edge_content(self.label, 'suffix')
        self.make_canonical()
    #
    def add_explicit(self):
        # 'self' is assumed to be in its canonical representation
        if self.is_explicit():
            return self.label
        p, l, child = self.tree.get_edge_content(self.label, self.word[self.pos])
        new_explicit_state = self.tree.add_new_vertex()
        self.tree.update_edge_content(self.label, self.word[p], (p, self.len, new_explicit_state))
        self.tree.update_edge_content(new_explicit_state, self.word[p + self.len], (p + self.len, l - self.len, child))
        return new_explicit_state
    #
    def add_leaf(self, position):
        # 'self' is assumed not to have any 'self.word[position]'-transition,
        # and to be in its canonical representation
        new_explicit_state = self.add_explicit()
        self.tree.update_edge_content(new_explicit_state, self.word[position],
            (position, self.leafs_length - position, 'leaf'))
            # (position, math.inf, 'leaf'))
        return new_explicit_state
    #
    def elongate(self, position):
        if self.is_explicit():
            self.move(self.label, position, 1)
        else:
            self.len += 1
        self.make_canonical()




def ukkonen(word):
    s = Implicit_state(word)
    for p in range(len(word)):
        if s.has_transition(p):
            s.elongate(p)
        elif s.is_root():
            s.add_leaf(p)
        else:
            explicit_state = s.add_leaf(p)
            s.move_to_suffix()
            while (not s.has_transition(p)) and (not s.is_root()):
                new_explicit_state = s.add_leaf(p)
                s.tree.update_edge_content(explicit_state, 'suffix', new_explicit_state)
                explicit_state = new_explicit_state
                s.move_to_suffix()
            if s.has_transition(p):
                s.tree.update_edge_content(explicit_state, 'suffix', s.label)
                s.elongate(p)
            else:
                s.tree.update_edge_content(explicit_state, 'suffix', s.root)
                s.add_leaf(p)
    return s