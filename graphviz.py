#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Marc-Olivier Buob <marc-olivier.buob@nokia-bell-labs.com>

import subprocess

def default_graphviz_style() -> str:
    FG_COLOR = "black"
    BG_COLOR = "transparent"
    return "graph[bgcolor = %(BG_COLOR)s fontcolor = %(FG_COLOR)s rankdir = LR]; " \
            "node[color = %(FG_COLOR)s fontcolor = %(FG_COLOR)s shape = circle]; " \
            "edge[color = %(FG_COLOR)s fontcolor = %(FG_COLOR)s]; " % locals()

def run_graphviz(graphviz_str :str, filename_out :str, graphviz_opts = ["-Tsvg"]) -> str:
    """
    Call graphviz on an input string to produce the corresponding image.
    By default the output image is a svg file.
    Args:
        graphviz_str: A string representing a graph in the graphviz format.
        filename_out: The path of the output file.
        graphviz_opts: The options passed to graphviz.
    """
    with open(filename_out, "w") as f:
        process = subprocess.Popen(["/usr/bin/dot"] + graphviz_opts, stdin = subprocess.PIPE, stdout = f)
        process.stdin.write(graphviz_str.encode("utf-8"))
        stdout, stderr = process.communicate()
        if stderr: # For debug purposes
            print(stderr, file = sys.stderr)

