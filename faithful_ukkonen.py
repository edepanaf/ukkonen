#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:      Elie De Panafieu  <elie.de_panafieu@nokia-bell-labs.com>
# Contributor: Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import string

"""
Python implementation of the algorithm of Ukkonen from 'On-line construction of suffix trees', Algorithmica.

The suffix tree, called 'tree', is built from an input string 'word' in O(n).

- 'tree' is a vector of dictionnaries, where each of them represents a node of the tree.
- Each state is represented by:
  - If state is a leaf:
    - An empty dictionnary.
  - Else (if this is an internal (= branching) node):
    - A dictionnary where each key-value pair represents an out-transition {a : (k, p, state)}
      - a: the first letter of the transition
      - (k, p, state): the triple characterize the transition, storing the substring word[k]word[k+1]...word[p] = w[k:p+1]
        - k: the index in 'word' where the substring starts.
        - p: the index in 'word' where the substring ends.
        - state: the index of the target node in 'tree'.
    - A special key, named "suffix", is injected in the dictionnary to store the eventual suffix link of the node.
      - In this algorithm, suffix links are only required for internal nodes.
      - A suffix link connect a state representing the suffix w[i:j] to a state representing w[i+1:j]

Most of the function rely on the notion of active point, which generalize the notion of current state in a Trie. Indeed
we may have to refer to a position in the suffix tree that lies in the middle of a transition.

The active point can be characterized by the triple (state, k, p):
  - If k <= p:
    - This means: walk from the explicit state 'state' according to the substring word[k]...word[p] i.e. w[k:p+1] in python.
    - This convention does not allow to design easily on the explicit 'state'. This is why we also define (state, k, p) if p < k
  - If k > p:
    - The substring represented by (k, p) is considered to be the empty word (\varepsilon).
    - (state, k, p) means that we point to 'state'.

Each state 's' corresponds to a factor of 'word', denoted by 'word(s)'.
It is not explicitly present in the tree.
If the letter 't' is in 'tree[s]' and 'tree[s][t] = (k, p, ss)', then 'word(ss) == word(s) + word[k:p+1]'.
'tree[s]['suffix']' corresponds to the factor 'word(s)[1:]'.
"""

BOTTOM = 0 # The parent node of the suffix tree root node.
ROOT = 1   # The root node of the suffix tree.

def create_new_state(tree :list) -> int:
    """
    Add a new state in the suffix tree.
    Args:
        tree: The list representing the suffix tree.
    Returns:
        The index of the state. The indexes starts from 0.
    """
    tree.append(dict())
    return len(tree) - 1

def test_and_split(word :str, tree :list, state :tuple, k :int, p :int, letter :chr) -> tuple:
    """
    Test whether a 'letter'-transition exists at the active point ('state', 'k', 'p').
    If not, create the explicit state at the active point and append the 'letter'-transition (tail).
    See https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf (p12)
    Args:
        word: The string containing the input word.
        tree: The list representing the suffix tree to update.
        (state, k, p): The active point.
        letter: The tested letter.
    Returns:
        A pair (has_transition, explicit_state) set as follows
            - has_transition: True iff the letter-transition already exists
            - explicit_state: The index of the node having the transition.
    """
    if state == BOTTOM:
        # This part was not in the paper. This represents the fact
        # that the states 'BOTTOM' and 'ROOT' are linked by all letters of the alphabet
        ret = (True, state)
    elif k <= p:
        # This means that '(k, p)' does not represent the empty word in 'word'
        # Retrieve the substring and the target node 'sstate'
        (kk, pp, sstate) = tree[state][word[k]]
        if letter == word[kk + p - k + 1]:
            # Tests whether 'state' is the end-point, ie if it has a 'letter'-transition.
            # 'kk + p - k + 1' always smaller than 'len(word)',
            # because the implicit state '(state, k, p)'
            # lies on an implicit path linking the states 'state' and 'sstate'
            ret = (True, state)
        else:
            # Split the ('state' -> 'sstate') arc by inserting  a new explicit state 'r_state'
            r_state = create_new_state(tree)
            tree[state][word[k]] = (kk, kk + p - k, r_state)
            tree[r_state][word[kk + p - k + 1]] = (kk + p - k + 1, pp, sstate)
            ret = (False, r_state)
    else:
        # If the pair of positions '(k, p)' represents the empty word,
        # then 'state' is the end-point iff it has a 'letter'-transition.
        ret = (letter in tree[state], state)
    return ret

def canonize(word :str, tree :list, state :tuple, k :int, p :int) -> tuple:
    """
    Canonize primitive.
    See https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf (p13).
    Args:
        word: The string containing the input word.
        tree: The list representing the suffix tree to update.
        (state, k, p): Non-canonized active point.
          - state: Non-canonized active state.
          - k: Non-canonized active edge. This is an index in 'word'.
          - p: Non-canonized active length. active_point = move(state, w[k:k+p])
    Returns:
        A pair (active_state, active_edge).
          - active_state: The canonized active state.
          - active_edge: The canonized active edge.
        Note: active_length = max(0, p - k).
    """
    if p < k:
        # then the pair of positions '(k, p)' represents the empty word,
        # and the state representation '(state, k, p)' is already canonical
        return (state, k)

    # Traverse the transition starting with word[k], and corresponding to w[kk:pp+1]
    # This reads up to (pp + 1 - kk) characters and update k consequently.
    # If k becomes lower than p, this means that state is canonize.
    kk, pp, sstate = tree[state][word[k]]
    while pp - kk <= p - k:
        k = k + pp - kk + 1
        state = sstate
        if k <= p:
            # Move to the next transition.
            kk, pp, sstate = tree[state][word[k]]
    return (state, k)

def update(word :str, tree :list, state :tuple, k :int, i :int) -> tuple:
    """
    Update primitive.
    See https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf (p12).
    Args:
        word: The string containing the input word.
        tree: The list reprensenting the suffix tree to update.
        state: The tuple representing the state involved in the active point.
        k: An integer such that w[k] is the first letter of the active edge.
        i: An integer indicating the number of character to be read along
            the active edge.
    Returns:
        A pair (state, k).
    """
    # '(state, k, i-1)' is the canonical reference for the active point
    oldr = ROOT
    is_end_point, r = test_and_split(word, tree, state, k, i - 1, word[i])

    # Travel along the boundary path while it is possible to append tail.
    # To do so:
    #   current root = active_point if explicit else its lowest ancestor (= active state).
    #   While the end point is not reached:
    #     Append the tail from the active point.
    #     If the transition already exists: the end point has been reached.
    #     Move to the next root through the suffix link of the current root
    #     Adapt the active point to conform to the new root (canonize).
    while not is_end_point:
        rr = create_new_state(tree)
        tree[r][word[i]] = (i, len(word) - 1, rr)
        # Should 'len(word)-1' be replaced by 'infinity'?
        if oldr != ROOT:
            tree[oldr]['suffix'] = r
        oldr = r
        state, k = canonize(word, tree, tree[state]['suffix'], k, i - 1)
        is_end_point, r = test_and_split(word, tree, state, k, i - 1, word[i])

    if oldr != ROOT:
        tree[oldr]['suffix'] = state

    return (state, k)

def ukkonen(word :str) -> list:
    """
    Build the suffix tree representing an input word.
    Args:
        word: A str instance. The word is supposed to be lower case.
    Returns:
        The list representing the suffix tree.
    """
    tree = [{letter:(0, 0, 1) for letter in string.ascii_lowercase}, {'suffix' : 0}]
    state = ROOT
    k = 0
    for i in range(len(word)):
        (state, k) = update(word, tree, state, k, i)
        (state, k) = canonize(word, tree, state, k, i)
    return tree

#-------------------------------------------------------------------------------------

from graphviz import run_graphviz, default_graphviz_style

def to_dot(word :str, tree :list) -> str:
    """
    Graphviz export.
    Args:
        word: A string containing the word used to build the suffix tree.
        tree: The list representing the suffix tree.
    Returns:
        The string in the graphviz format representing the suffix tree.
    """
    s = "digraph G { %s" % default_graphviz_style()

    # Vertices
    for u, d in enumerate(tree):
        if u == BOTTOM:
            s += "  %s [label = <&perp;>];\n" % u
        elif u == ROOT:
            s += "  %s [label = <&Lambda;>];\n" % u
        else:
            s += "  %s [label = <%s> shape = \"doublecircle\"];\n" % (u, u)

    # Arcs
    for u, d in enumerate(tree):
        if u == BOTTOM:
            s += "  %s -> %s [label = <&Sigma;>];\n" % (BOTTOM, ROOT)
            continue

        for (a, t) in d.items():
            if a == "suffix": continue
            (i, j, v) = t

            # Transitions
            infix = word[i:j+1]
            s += "  %(u)s -> %(v)s [label = <%(infix)s>];\n" % locals()

            # Suffix links
            #if node.slink != None:
            #    s += "%s -> %s [style=\"dotted\"];" % (u, node.slink)

    s += "}"
    return s


if __name__ == '__main__':
    word = "bananas" # "cacao"
    tree = ukkonen(word)
    run_graphviz(to_dot(word, tree), "out.svg")
