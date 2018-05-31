#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:      Elie De Panafieu  <elie.de_panafieu@nokia-bell-labs.com>


"""
Ukkonen's algorithm is described in 'On-line construction of suffix trees', Algorithmica.
We present a short implementation (50 lines without the comments), 
slightly different from the original.
This file, written by Elie de Panafieu, is available on github.

'tree' is a list of dictionnaries that represents a rooted tree,
with some additional edges, called the suffix links and described later.
The edges of this tree are marked by a string that is a factor of 'word'.
It is represented by a couple of integers '(position, length)',
and this string is equal to 'word[position: position + length]'.

For each edge '(position, length)' from a node 's' to a child 't',
the dictionnary corresponding to 's', in the list 'tree',
associates to the first letter of the word
represented by (position, length) the triplet (position, length, t),
so we have 'tree[s][word[position]] == (position, length, t)'.
Only the internal nodes are present in the list of dictionnaries 'tree'.
If 't' is a leaf, then we have instead
'tree[s][word[position]] == (position, math.inf, "leaf")',
where 'math.inf' is equal to + infinity, with the usual conventions.
The root of the tree is the first element of 'tree'.

Each internal node 's' of the tree corresponds,
implicitly, to a string, denoted by 'factor(s)',
and equal to the concatenation of the edge's strings
on the path from the root to the node 's'.
Inversely, any factor of 'word' that has at least two occurrences
followed by different letters corresponds to a node.
The leaves of the tree correspond to the suffices of 'word'
that have no other occurrences as factors of 'word'.
In particular, a factor of 'word' that is a suffix
and also appears only once somewhere else in 'word'
does not correspond to an internal node.

If one wants that the suffices correspond exactly to the leaves,
a classical solution is to add at the end of the word
a letter that occurres nowhere else.

The tree has additional edges, called the 'suffix links'.
The internal node 's' corresponding to the factor 'factor(s)',
points to the node 't' that corresponds to 'factor(s)' whithout its first letter
(observe that 't' is necessary an internal node as well).
To represent this additional edge in the list of dictionnaries 'tree',
we have 'tree[s]["suffix"] == t'.

In addition to the suffix tree, the algorithm outputs three variables
'node', 'position', and 'length', such that
- the string 'factor(node) + word[position, position + length]' is equal to
the longest suffix that has at least one other occurrence in 'word',
- 'length' is the minimal integer to satisfy the previous property.
Thus, the edge starting at 'node' and that has
a string 'S' on it starting with the letter 'word[position]'
is such that the length of 'S' is stricly smaller than 'length'.
- if 'length' is strictly positive, then the first element
of the triplet 'tree[node][word[position]]' is equal to 'position'.
If 'length == 0', then 'position' has no particular constraint or meaning.

The algorithm is an online algorithm:
it computes 'node', 'position', 'length', and 'tree' for 'word[:p]'
for 'p' from '0' to 'len(word)'.

An "implicit node" is defined by a tree, a node, a position, and a length.
It corresponds to the factor of word 'factor(node) + word[position: position + length]'.
An implicit node is said to be "explicit" if 'length == 0'.
It is said to be "canonical" iff it is either explicit,
or the following two conditions are satisfied.
Let '(position2, length_node_child, child)' denote the triplet 'tree[node][word[position]]',
then 'position2 == position' and 'length_node_child < length'.

Some interesting strings to test the algorithm:

>>> ukkonen('abcabxabcd')
(0, 0, 0, [{'a': (0, 2, 1), 'suffix': 0, 'b': (1, 1, 2), 'c': (2, 1, 5), 'x': (5, inf, 'leaf'), 'd': (9, inf, 'leaf')}, {'x': (5, inf, 'leaf'), 'c': (2, 1, 3), 'suffix': 2}, {'x': (5, inf, 'leaf'), 'c': (2, 1, 4), 'suffix': 0}, {'d': (9, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 4}, {'d': (9, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 5}, {'d': (9, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 0}])

>>> ukkonen('abcacdae')
(0, 0, 0, [{'a': (0, 1, 1), 'suffix': 0, 'b': (1, inf, 'leaf'), 'c': (2, 1, 2), 'd': (5, inf, 'leaf'), 'e': (7, inf, 'leaf')}, {'c': (4, inf, 'leaf'), 'b': (1, inf, 'leaf'), 'suffix': 0, 'e': (7, inf, 'leaf')}, {'d': (5, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 0}])

ukkonen('aabaabbc')
(0, 0, 0, [{'a': (0, 1, 1), 'suffix': 0, 'b': (2, 1, 4), 'c': (7, inf, 'leaf')}, {'b': (2, 1, 3), 'a': (1, 2, 2), 'suffix': 0}, {'b': (6, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 3}, {'b': (6, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 4}, {'b': (6, inf, 'leaf'), 'a': (3, inf, 'leaf'), 'suffix': 0, 'c': (7, inf, 'leaf')}])

>>> ukkonen('abcabdabc')
(1, 2, 1, [{'a': (0, 2, 1), 'suffix': 0, 'b': (1, 1, 2), 'c': (2, inf, 'leaf'), 'd': (5, inf, 'leaf')}, {'d': (5, inf, 'leaf'), 'c': (2, inf, 'leaf'), 'suffix': 2}, {'d': (5, inf, 'leaf'), 'c': (2, inf, 'leaf'), 'suffix': 0}])

"""


import math

def ukkonen(word):
  ROOT, SUFFIX, LEAF, INFINITY = 0, 'suffix', 'leaf', math.inf
  tree, node, position, length, length_node_child, child = [{}], ROOT, 0, 0, 0, 0
  for p in range(len(word)):
    letter = word[p]
    previous_node = ROOT
    # The next loop treats canonical non-explicit nodes which do not have a 'letter' continuation.
    while length > 0 and letter != word[position + length]:
      # creation of a new node
      _, length_node_child, child = tree[node][word[position]] # We manage the variables so that '_' should be equal to 'position'.
      new_node = len(tree)
      tree.append({letter: (p, INFINITY, LEAF),
        word[position + length]: (position + length, length_node_child - length, child)})
      tree[node][word[position]] = (position, length, new_node)
      # addition of the suffix link
      tree[previous_node][SUFFIX] = new_node
      previous_node = new_node
      # move to the suffix non-canonical implicit node
      if node == ROOT:
        position += 1
        length -= 1
      else:
        node = tree[node][SUFFIX]
      # canonization of the implicit node
      _, length_node_child, child = tree[node][word[position]] # Here, '_' can be different from 'position'.
      while length_node_child <= length:
        node = child
        position += length_node_child
        length -= length_node_child
        _, length_node_child, child = tree[node][word[position]] # Here, '_' can be different from 'position'.
      # If the reached node is implicit, to finish the canonization, we set 'position' to its correct value.
      if length > 0:
        position, _, _ = tree[node][word[position]]
    # The next loop deals with explicit nodes which are not the root and do not have a 'letter' transition.
    while node != ROOT and letter not in tree[node] and length == 0:
      # addition of the leaf
      tree[node][letter] = (p, INFINITY, LEAF)
      # creation of the suffix link
      tree[previous_node][SUFFIX] = node
      # moving to the suffix
      node = tree[node][SUFFIX]
    # The case of the root without a 'letter' transition is treated in the next conditional.
    if node == ROOT and letter not in tree[ROOT]:
      # addition of the leaf
      tree[ROOT][letter] = (p, INFINITY, LEAF)
      # The new longest suffix with at least two occurrences is the empty word, so 'length' is set to '0'.
      length = 0
      # addition of the suffix link
      tree[previous_node][SUFFIX] = ROOT
    # Finally, we consider the cases where we have reached an implicit or explicit node which has a 'letter' transition.
    else:
      # This conditional deals with explicit nodes.
      if length == 0:
        # addition of a suffix link
        tree[previous_node][SUFFIX] = node
        position, length_node_child, child = tree[node][letter]
      # This 'else' deals with non-explicit nodes.
      else:
        position, length_node_child, child = tree[node][word[position]]
      # The addition of 'letter' increases the length, and the node becomes non-explicit and possibly non-canonical.
      length += 1
      # canonization of the new implicit node
      if length_node_child == length:
        node = child
        length = 0
  # Cleaning the values that have no particular meaning.
  tree[ROOT][SUFFIX] = ROOT
  if length == 0:
    position = 0
  return node, position, length, tree


# Test the previous implementation of Ukkonen's algorithm
# on a random string of size 'n' on an alphabet of size 'alphabet_size' ('3' by default).
"""
import random

def random_test(n, alphabet_size=3):
  alphabet = list('abcdefghijklmnopqrstuvwxyz')[:alphabet_size]
  s = ''.join([random.choice(alphabet) for i in range(n)])  
  return (s, ukkonen(s))

"""
