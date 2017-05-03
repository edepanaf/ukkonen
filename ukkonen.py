

"""
Python implementation of the algorithm of Ukkonen from 'On-line construction of suffix trees', Algorithmica.

Given a word 'word', a suffix-tree 'tree' is represented as a list indexed by 'states'.

For each state 's', 'tree[s]' is a dictionary, which keys are some letters and the string 'suffix'.
'suffix' is associated to a state.
Each letter is linked to triplet '(p,k,state)'
where 'p' and 'k' represent positions in 'word' and 'state' is a state of the tree.

Each state 's' corresponds to a factor of 'word', denoted by 'word(s)'.
It is not explicitly present in the tree.
If the letter 't' is in 'tree[s]' and 'tree[s][t] = (k, p, ss)',
then 'word(ss) == word(s) + word[k:p+1]'.
'tree[s]['suffix']' corresponds to the factor 'word(s)[1:]'.
"""

bottom = 0
root = 1


def create_new_state(tree):
    tree.append({})
    return len(tree)-1



def test_and_split(word, tree, state, k, p, letter):
    if state == bottom:
        # this part was not in the paper. This represents the fact
        # that the states 'bottom' and 'root' are linked by all letters of the alphabet
        return (True, state)
    if k <= p:
        # this means that the pair of positions '(k, p)' does not represent the empty word in 'word'
        kk, pp, sstate = tree[state][word[k]]
        if letter == word[kk + p - k + 1]:
            # tests whether 'state' is the end-point, ie if it has a 'letter'-transition.
            # 'kk + p - k + 1' always smaller than 'len(word)',
            # because the implicit state '(state, k, p)'
            # lies on an implicite path linking the states 'state' and 'sstate'
            return (True, state)
        # otherwise, a new explicit state 'r_state' is created
        # between 'state' and 'sstate'
        r_state = create_new_state(tree)
        tree[state][word[k]] = (kk, kk + p - k, r_state)
        tree[r_state][word[kk + p - k + 1]] = (kk + p - k + 1, pp, sstate)
        return (False, r_state)
    return (letter in tree[state], state)
    # if the pair of positions '(k, p)' represents the empty words,
    # then 'state' is the end-point iff it has a 'letter'-transition.



def canonize(word, tree, state, k, p):
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



def update(word, tree, state, k, i):
    # '(state, k, i-1)' is the canonical reference for the active point
    oldr = root
    is_end_point, r = test_and_split(word, tree, state, k, i-1, word[i])
    while not is_end_point:
        rr = create_new_state(tree)
        tree[r][word[i]] = (i, len(word)-1, rr)
        # should 'len(word)-1' be replaced by 'infinity'?
        if oldr != root:
            tree[oldr]['suffix'] = r
        oldr = r
        state, k = canonize(word, tree, tree[state]['suffix'], k, i-1)
        is_end_point, r = test_and_split(word, tree, state, k, i-1, word[i])
    if oldr != root:
        tree[oldr]['suffix'] = state
    return (state, k)



def ukkonen(word):
    tree = [{letter:(0,0,1) for letter in 'abcdefghijklmnopqrstuvwxyz'}, {'suffix':0}]
    state = root
    k = 0
    for i in range(len(word)):
        state, k = update(word, tree, state, k, i)
        state, k = canonize(word, tree, state, k, i)
    return tree

""" test
ukkonen('cacao')
"""
