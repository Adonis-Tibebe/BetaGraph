"""Candidate Boolean programs and the three-bit parity truth table."""

import itertools


rows = list(itertools.product([0, 1], repeat=3))
target = tuple(a ^ b ^ c for a, b, c in rows)


# Candidates use the same nested-tuple AST shape as training-3-test/test.py.
candidates = {
	1: ("AND", "A", ("OR", "B", "C")),
	2: ("OR", ("AND", "A", "B"), "C"),
	3: ("NOT", ("AND", "A", ("OR", "B", "C"))),
	4: ("OR", ("NOT", "A"), ("AND", "B", "C")),
	5: ("AND", ("OR", "A", "B"), ("NOT", "C")),
	6: ("OR", ("AND", "A", ("NOT", "B")), ("AND", "B", "C")),
	7: ("AND", ("NOT", "A"), ("OR", "B", ("NOT", "C"))),
	8: ("OR", ("NOT", ("AND", "A", "B")), "C"),
	9: ("AND", ("OR", "A", ("NOT", "B")), ("OR", "B", "C")),
	10: ("NOT", ("OR", ("AND", "A", "C"), "B")),
	11: ("OR", ("AND", "A", "B"), ("AND", ("NOT", "A"), "C")),
	12: ("AND", ("OR", "A", "C"), ("OR", ("NOT", "B"), "C")),
	13: ("OR", ("AND", ("NOT", "A"), "B"), ("AND", "A", "C")),
	14: ("NOT", ("AND", ("OR", "A", "B"), ("NOT", "C"))),
	15: ("AND", ("NOT", ("OR", "A", "C")), ("OR", "B", "C")),
	16: ("OR", ("AND", "A", ("NOT", "C")), ("AND", ("NOT", "B"), "C")),
	17: ("AND", ("OR", ("NOT", "A"), "B"), ("NOT", ("AND", "B", "C"))),
	18: ("OR", ("NOT", ("OR", "A", "B")), ("AND", "A", "C")),
	19: ("AND", ("OR", "A", ("AND", "B", "C")), ("OR", ("NOT", "B"), "C")),
	20: ("OR", ("AND", "A", ("NOT", "B")), ("AND", ("OR", "B", "C"), ("NOT", "A"))),
}


if __name__ == "__main__":
	print("Rows:", rows)
	print("Target:", target)
	print("Candidate count:", len(candidates))
	print("Candidate 1:", candidates[1])