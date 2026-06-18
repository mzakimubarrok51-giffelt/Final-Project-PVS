"""Sanity check: brute-force DFS (same logic as Z3 model) over CASES."""

CASES = [
    {"name": "① 3 kubus — dasar", "s": [1, 0, 2], "t": [0, 0, 0],
     "A": [[1, 0, 0], [1, 1, 0], [0, 1, 1]]},
    {"name": "② 5 kubus — bidiagonal", "s": [2, 1, 3, 0, 2], "t": [0, 0, 0, 0, 0],
     "A": [[1, 1, 0, 0, 0], [0, 1, 1, 0, 0], [0, 0, 1, 1, 0], [0, 0, 0, 1, 1], [0, 0, 0, 0, 1]]},
    {"name": "③ 3 kubus — full connect", "s": [0, 0, 0], "t": [2, 2, 2],
     "A": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]},
    {"name": "④ 4 kubus — cyclic", "s": [2, 1, 0, 3], "t": [0, 0, 0, 0],
     "A": [[1, 0, 0, 1], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]},
    {"name": "⑤ UNSAT demo (2 kubus)", "s": [0, 0], "t": [1, 3],
     "A": [[1, 1], [1, 1]]},
]


def brute_solve(s, t, A):
    n = len(s)
    best, best_total = None, None
    def dfs(idx, x):
        nonlocal best, best_total
        if idx == n:
            for k in range(n):
                total = s[k] + sum(A[k][j] * x[j] for j in range(n))
                if total % 4 != t[k]:
                    return
            tot = sum(x)
            if best is None or tot < best_total:
                best, best_total = list(x), tot
            return
        for v in range(4):
            x[idx] = v
            dfs(idx + 1, x)
    dfs(0, [0] * n)
    return best, best_total


for c in CASES:
    sol, total = brute_solve(c["s"], c["t"], c["A"])
    if sol is None:
        print(f"{c['name']}: UNSAT")
    else:
        print(f"{c['name']}: x = {sol} (total clicks = {total})")
