import itertools, math
from functools import lru_cache
import networkx as nx

# ----------------------------
# 1) Example graph
# ----------------------------
G = nx.wheel_graph(7)  # nodes 0..6

nodes = list(G.nodes())

# -----------------------------------------------
# 2) Exact treewidth by brute-force elimination
# -----------------------------------------------
def elimination_width_and_bags(G, order):
    adj = {v: set(G.neighbors(v)) for v in G.nodes()}
    bags = []
    width = 0
    for v in order:
        N = set(adj[v])
        width = max(width, len(N))
        bag = set([v]) | N
        bags.append((v, bag, N))
        for a in N:
            for b in N:
                if a != b:
                    adj[a].add(b)
        for u in N:
            adj[u].discard(v)
        adj[v].clear()
    return width, bags

best_tw = math.inf
best_order_tw = None
best_bags_tw = None

for order in itertools.permutations(nodes):
    w, bags = elimination_width_and_bags(G, order)
    if w < best_tw:
        best_tw = w
        best_order_tw = order
        best_bags_tw = bags

pos = {v: i for i, v in enumerate(best_order_tw)}
bag_ids = {v: i for i, v in enumerate(best_order_tw)}

edges_td = []
bags_td = [None] * len(nodes)
for v, bag, N in best_bags_tw:
    bags_td[bag_ids[v]] = sorted(bag)
    later_neighbors = [u for u in N if pos[u] > pos[v]]
    if later_neighbors:
        parent = min(later_neighbors, key=lambda u: pos[u])
        edges_td.append((bag_ids[v], bag_ids[parent]))

# -----------------------------------------------
# 3) Exact pathwidth by brute-force vertex separation
# -----------------------------------------------
def vertex_separation(G, order):
    prefix = set()
    max_sep = 0
    for v in order:
        prefix.add(v)
        boundary = {u for u in prefix if any((w not in prefix) for w in G.neighbors(u))}
        max_sep = max(max_sep, len(boundary))
    return max_sep

best_pw = math.inf
best_order_pw = None
for order in itertools.permutations(nodes):
    sep = vertex_separation(G, order)
    if sep < best_pw:
        best_pw = sep
        best_order_pw = order

order_pw = list(best_order_pw)
B_path = []
prefix = set()
for v in order_pw:
    boundary = {u for u in prefix if any((w not in prefix) for w in G.neighbors(u))}
    bag = sorted(set(boundary) | {v})
    B_path.append(bag)
    prefix.add(v)

# -----------------------------------------------
# 4) Exact treedepth (adds this part)
# -----------------------------------------------
def height(tree):
    r, ch = tree
    if not ch:
        return 1
    return 1 + max(height(t) for t in ch)

@lru_cache(None)
def td_and_forest(S_fro):
    S = set(S_fro)
    if not S:
        return 0, []  # empty forest

    H = G.subgraph(S)
    comps = [tuple(sorted(c)) for c in nx.connected_components(H)]
    if len(comps) > 1:
        sub = [td_and_forest(tuple(c)) for c in comps]
        td_val = max(t for t, _ in sub)
        forest = []
        for _, f in sub:
            forest.extend(f)
        return td_val, forest

    best_td = None
    best_root = None
    best_children = None

    for v in S:
        S2 = tuple(sorted(S - {v}))
        H2 = G.subgraph(S2)
        comps2 = [tuple(sorted(c)) for c in nx.connected_components(H2)]

        children = []
        max_child_td = 0
        for c in comps2:
            tdc, fc = td_and_forest(tuple(c))
            max_child_td = max(max_child_td, tdc)
            children.extend(fc)

        td_here = 1 + max_child_td
        if best_td is None or td_here < best_td:
            best_td = td_here
            best_root = v
            best_children = children

    return best_td, [(best_root, best_children)]

# -----------------------------------------------
# 5) TikZ generators
# -----------------------------------------------
def latex_bag(bag):
    return "\\{" + ",".join(map(str, bag)) + "\\}"

def tikz_graph_wheel(G):
    import math
    cycle = [1, 2, 3, 4, 5, 6]
    lines = []
    lines.append("\\begin{tikzpicture}[scale=1.0, every node/.style={circle, draw, inner sep=1.5pt, font=\\small}]")
    lines.append("  \\node (c) at (0,0) {0};")
    for i, v in enumerate(cycle):
        angle = 2 * math.pi * i / len(cycle)
        x, y = 2.2 * math.cos(angle), 2.2 * math.sin(angle)
        lines.append(f"  \\\\node ({v}) at ({x:.3f},{y:.3f}) {{{v}}};")
    for u, v in G.edges():
        uu = "c" if u == 0 else str(u)
        vv = "c" if v == 0 else str(v)
        lines.append(f"  \\\\draw ({uu}) -- ({vv});")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)

def tikz_tree_decomposition(bags, edges):
    lines = []
    lines.append("\\begin{tikzpicture}[every node/.style={draw, rounded corners, font=\\scriptsize, align=center, inner sep=2pt}]")
    for i, bag in enumerate(bags):
        lines.append(f"  \\\\node (b{i}) at (0.00,{-2.0*i:.2f}) {{{latex_bag(bag)}}};")
    for a, b in edges:
        lines.append(f"  \\\\draw (b{a}) -- (b{b});")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)

def tikz_path_decomposition(bags):
    lines = []
    lines.append("\\begin{tikzpicture}[every node/.style={draw, rounded corners, font=\\scriptsize, align=center, inner sep=2pt}]")
    for i, bag in enumerate(bags):
        lines.append(f"  \\\\node (p{i}) at ({4.0*i:.2f},0) {{{latex_bag(bag)}}};")
        if i > 0:
            lines.append(f"  \\\\draw (p{i-1}) -- (p{i});")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)

def tikz_rooted_tree(tree):
    r, children = tree
    s = f"node{{{r}}}"
    for ch in children:
        s += " child {" + tikz_rooted_tree(ch) + "}"
    return s

def tikz_treedepth_forest(forest):
    lines = []
    lines.append("\\begin{tikzpicture}[grow=down, level distance=12mm, sibling distance=14mm, every node/.style={circle, draw, inner sep=1.5pt, font=\\small}]")
    if len(forest) == 1:
        lines.append("  \\\\" + tikz_rooted_tree(forest[0]) + ";")
    else:
        for i, t in enumerate(forest):
            lines.append(f"  \\\\begin{{scope}}[shift={{({i*4.0},0)}}]")
            lines.append("    \\\\" + tikz_rooted_tree(t) + ";")
            lines.append("  \\\\end{scope}")
    lines.append("\\end{tikzpicture}")
    return "\n".join(lines)

# -----------------------------------------------
# 6) Print everything
# -----------------------------------------------
print("Exact treewidth =", best_tw)
print("Exact pathwidth  =", best_pw)

td_val, forest = td_and_forest(tuple(sorted(G.nodes())))
print("Exact treedepth  =", td_val)
print("Treedepth decomposition height check =", max(height(t) for t in forest) if forest else 0)

print("\n----- TikZ: graph -----")
print(tikz_graph_wheel(G))

print("\n----- TikZ: tree decomposition -----")
print(tikz_tree_decomposition(bags_td, edges_td))

print("\n----- TikZ: path decomposition -----")
print(tikz_path_decomposition(B_path))

print("\n----- TikZ: treedepth decomposition -----")
print(tikz_treedepth_forest(forest))
