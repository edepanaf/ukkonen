#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:      Elie De Panafieu  <elie.de_panafieu@nokia-bell-labs.com>
# Contributor: Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import string

"""
Python implementation of the algorithm of Ukkonen from 'On-line construction of suffix trees', Algorithmica.

Given a word 'word', a suffix-tree 'tree' is represented as a list indexed by 'states'.

For each state 's', 'tree[s]' is a dictionary, which keys are some letters and the string 'suffix'.
'suffix' is associated to a state.
Each letter is linked to triplet '(p, k, state)'
where 'p' and 'k' represent positions in 'word' and 'state' is a state of the tree.

Each state 's' corresponds to a factor of 'word', denoted by 'word(s)'.
It is not explicitly present in the tree.
If the letter 't' is in 'tree[s]' and 'tree[s][t] = (k, p, ss)',
then 'word(ss) == word(s) + word[k:p+1]'.
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
    return len(tree)-1

def test_and_split(word :str, tree :list, state :tuple, k :int, p :int, letter :chr) -> tuple:
    """
    Canonize primitive.
    See https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf (p12)
    Args:
        word: The string containing the input word.
        tree: The list reprensenting the suffix tree to update.
        state:
        k:
        p:
    Returns:
        A pair (bool, tuple).
    """
    if state == BOTTOM:
        # This part was not in the paper. This represents the fact
        # that the states 'BOTTOM' and 'ROOT' are linked by all letters of the alphabet
        ret = (True, state)
    elif k <= p:
        # This means that the pair of positions '(k, p)' does not represent the empty word in 'word'
        kk, pp, sstate = tree[state][word[k]]
        if letter == word[kk + p - k + 1]:
            # Tests whether 'state' is the end-point, ie if it has a 'letter'-transition.
            # 'kk + p - k + 1' always smaller than 'len(word)',
            # because the implicit state '(state, k, p)'
            # lies on an implicite path linking the states 'state' and 'sstate'
            ret = (True, state)
        else:
            # Otherwise, a new explicit state 'r_state' is created
            # between 'state' and 'sstate'
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
        tree: The list reprensenting the suffix tree to update.
        state:
        k:
        p:
    Returns:
        A pair (state, k).
    """
    if p < k:
        # then the pair of positions '(k, p)' represents the empty word,
        # and the state representation '(state, k, p)' is already canonical
        return (state, k)

    kk, pp, sstate = tree[state][word[k]]
    while pp - kk <= p - k:
        k = k + pp - kk + 1
        state = sstate
        if k <= p:
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
    word = "ababc" # "cacao"
    tree = ukkonen(word)
    run_graphviz(to_dot(word, tree), "out.svg")
