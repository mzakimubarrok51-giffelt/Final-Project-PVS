"""
Inazuma Cube 3D - Z3 Solver Backend
=====================================
Constraint Satisfaction puzzle solver using Z3 Theorem Prover.

Puzzle model
------------
There are n cubes, each holding a state in Z_4 = {0,1,2,3}.
Clicking cube j increments the state of every cube k for which A[k][j] == 1
(mod 4), including j itself if A[j][j] == 1.

Given:
  - s[k]: initial state of cube k
  - t[k]: target state of cube k
  - A[k][j]: adjacency / influence matrix (0 or 1)
  - x[j]: number of times cube j is clicked (x[j] >= 0)

We need, for every k:
  s[k] + sum_j A[k][j] * x[j]  ==  t[k]   (mod 4)

Z3 is used to find an assignment of x[j] (non-negative integers) satisfying
all constraints, minimizing the total number of clicks sum(x[j]).
If no assignment exists, the puzzle is UNSAT.

Run
---
  pip install flask z3-solver
  python solver.py

Then open index.html (served at http://localhost:5000/) in a browser.
"""

from flask import Flask, jsonify, render_template, request
from z3 import Int, Optimize, If, Sum, sat

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Puzzle case definitions (mirrors the CASES array in the Three.js frontend)
# ---------------------------------------------------------------------------
CASES = [
    {
        "name": "① 3 kubus — dasar",
        "s": [1, 0, 2],
        "t": [0, 0, 0],
        "A": [[1, 0, 0],
              [1, 1, 0],
              [0, 1, 1]],
    },
    {
        "name": "② 5 kubus — bidiagonal",
        "s": [2, 1, 3, 0, 2],
        "t": [0, 0, 0, 0, 0],
        "A": [[1, 1, 0, 0, 0],
              [0, 1, 1, 0, 0],
              [0, 0, 1, 1, 0],
              [0, 0, 0, 1, 1],
              [0, 0, 0, 0, 1]],
    },
    {
        "name": "③ 3 kubus — full connect",
        "s": [0, 0, 0],
        "t": [2, 2, 2],
        "A": [[1, 1, 1],
              [1, 1, 1],
              [1, 1, 1]],
    },
    {
        "name": "④ 4 kubus — cyclic",
        "s": [2, 1, 0, 3],
        "t": [0, 0, 0, 0],
        "A": [[1, 0, 0, 1],
              [1, 1, 0, 0],
              [0, 1, 1, 0],
              [0, 0, 1, 1]],
    },
    {
        "name": "⑤ UNSAT demo (2 kubus)",
        "s": [0, 0],
        "t": [1, 3],
        "A": [[1, 1],
              [1, 1]],
    },
]

# Upper bound for click counts per cube. Since everything is mod 4,
# x[j] in [0, 3] is always sufficient to reach any residue class,
# and minimizing sum(x[j]) will never need to go higher.
MAX_CLICKS = 3


def solve_case(case: dict):
    """
    Solve a single puzzle case with Z3.

    Returns a dict:
      { "sat": True,  "solution": [x0, x1, ...], "total_clicks": int }
    or
      { "sat": False }
    """
    s = case["s"]
    t = case["t"]
    A = case["A"]
    n = len(s)

    opt = Optimize()

    # Decision variables: number of clicks for each cube, bounded.
    x = [Int(f"x_{j}") for j in range(n)]
    for j in range(n):
        opt.add(x[j] >= 0)
        opt.add(x[j] <= MAX_CLICKS)

    # Modular constraint for every cube k:
    #   (s[k] + sum_j A[k][j]*x[j]) mod 4 == t[k]
    # Z3's Int has no native mod-on-arithmetic-expression issue here since
    # '%' works for integers with non-negative operands (our sums are >= 0).
    for k in range(n):
        total = s[k] + Sum([A[k][j] * x[j] for j in range(n)])
        opt.add(total % 4 == t[k])

    # Objective: minimize total number of clicks.
    total_clicks = Sum(x)
    opt.minimize(total_clicks)

    if opt.check() == sat:
        m = opt.model()
        solution = [m.evaluate(x[j]).as_long() for j in range(n)]
        return {
            "sat": True,
            "solution": solution,
            "total_clicks": sum(solution),
        }
    else:
        return {"sat": False}


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/cases")
def api_cases():
    """Return all puzzle case definitions (without solving)."""
    return jsonify([
        {"name": c["name"], "s": c["s"], "t": c["t"], "A": c["A"]}
        for c in CASES
    ])


@app.route("/api/solve/<int:case_idx>")
def api_solve(case_idx):
    """Solve a built-in case by index."""
    if case_idx < 0 or case_idx >= len(CASES):
        return jsonify({"error": "invalid case index"}), 400
    result = solve_case(CASES[case_idx])
    return jsonify(result)


@app.route("/api/solve_custom", methods=["POST"])
def api_solve_custom():
    """
    Solve a custom puzzle definition posted as JSON:
      { "s": [...], "t": [...], "A": [[...], ...] }
    """
    data = request.get_json(force=True)
    s, t, A = data.get("s"), data.get("t"), data.get("A")

    if not (isinstance(s, list) and isinstance(t, list) and isinstance(A, list)):
        return jsonify({"error": "s, t, A must be lists"}), 400
    n = len(s)
    if len(t) != n or len(A) != n or any(len(row) != n for row in A):
        return jsonify({"error": "dimension mismatch between s, t, A"}), 400

    result = solve_case({"s": s, "t": t, "A": A})
    return jsonify(result)


if __name__ == "__main__":
    # Quick CLI self-test of all cases before starting the server
    print("=== Self-test: solving all built-in cases with Z3 ===")
    for i, c in enumerate(CASES):
        r = solve_case(c)
        if r["sat"]:
            print(f"{c['name']}: x = {r['solution']}  (total clicks = {r['total_clicks']})")
        else:
            print(f"{c['name']}: UNSAT")
    print("======================================================")

    # For local presentation: just run `python solver.py` -> http://localhost:5000
    # For deployment (Render/Railway/etc.), the PORT env var is provided by the
    # platform and gunicorn is used instead (see Procfile), so this block is
    # only used for local/dev runs.
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
