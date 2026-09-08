"""Evaluate and score Boolean candidate programs represented as nested tuples."""

import sys
from pathlib import Path

if __package__ in {None, ""}:
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import PLN_K


def eval_tree(node, env):
	"""Evaluate a nested tuple AST against Boolean values for A, B, and C."""
	if isinstance(node, str):
		return env[node]
	operator = node[0]
	if operator == "NOT":
		return not eval_tree(node[1], env)
	if operator == "AND":
		return eval_tree(node[1], env) and eval_tree(node[2], env)
	if operator == "OR":
		return eval_tree(node[1], env) or eval_tree(node[2], env)
	raise ValueError(f"Unknown operator: {operator}")


def evaluate_candidate(tree, rows, target, pln_k=PLN_K):
	"""Return direct evidence and Beta parameters for one candidate."""
	matches = 0
	for (a, b, c), expected in zip(rows, target):
		environment = {"A": bool(a), "B": bool(b), "C": bool(c)}
		if bool(eval_tree(tree, environment)) == bool(expected):
			matches += 1

	total = len(rows)
	failures = total - matches
	alpha = 1 + matches
	beta = 1 + failures
	strength = alpha / (alpha + beta)
	confidence = total / (total + pln_k)
	return {
		"successes": matches,
		"failures": failures,
		"strength": strength,
		"confidence": round(confidence, 3),
		"alpha": alpha,
		"beta": beta,
	}


def evaluate_candidates(candidate_data, rows, target, pln_k=PLN_K):
	"""Evaluate every candidate while preserving its identifier."""
	return {
		candidate_id: evaluate_candidate(tree, rows, target, pln_k)
		for candidate_id, tree in candidate_data.items()
	}


if __name__ == "__main__":
	from data.candidates import candidates, rows, target

	print("Candidate evidence:")
	for candidate_id, evidence in evaluate_candidates(candidates, rows, target).items():
		print(candidate_id, evidence)