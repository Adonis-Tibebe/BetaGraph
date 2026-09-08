"""Exhaustive co-occurrence scoring for candidate sub-expression pairs."""

import itertools
import sys
from pathlib import Path

if __package__ in {None, ""}:
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import PLN_K
from src.subexpressions import all_subexpressions


def candidate_subexpressions(candidate_data):
	"""Return canonical sub-expression sets keyed by candidate ID."""
	return {
		candidate_id: all_subexpressions(tree)
		for candidate_id, tree in candidate_data.items()
	}


def generate_pairs(subexpressions_by_candidate):
	"""Generate every distinct pair that co-occurs in at least one candidate."""
	pairs = set()
	for expressions in subexpressions_by_candidate.values():
		for pair in itertools.combinations(sorted(expressions), 2):
			pairs.add(pair)
	return sorted(pairs)


def score_pair(pair, subexpressions_by_candidate, candidate_evidence, pln_k=PLN_K):
	"""Score one pair using the evidence of candidates containing both members."""
	containing_candidates = [
		candidate_id
		for candidate_id, expressions in subexpressions_by_candidate.items()
		if pair[0] in expressions and pair[1] in expressions
	]
	if not containing_candidates:
		return None

	strength = sum(
		candidate_evidence[candidate_id]["strength"]
		for candidate_id in containing_candidates
	) / len(containing_candidates)
	n = len(containing_candidates)
	confidence = n / (n + pln_k)
	return {
		"strength": strength,
		"confidence": confidence,
		"n": n,
		"containing_candidates": containing_candidates,
	}


def score_all_pairs(
	candidate_data, candidate_evidence, pln_k=PLN_K
):
	"""Return the complete, unfiltered co-occurrence table."""
	subexpressions_by_candidate = candidate_subexpressions(candidate_data)
	return {
		pair: score_pair(
			pair,
			subexpressions_by_candidate,
			candidate_evidence,
			pln_k,
		)
		for pair in generate_pairs(subexpressions_by_candidate)
	}


if __name__ == "__main__":
	from data.candidates import candidates, rows, target
	from src.parsing import evaluate_candidates

	evidence = evaluate_candidates(candidates, rows, target)
	table = score_all_pairs(candidates, evidence)
	sorted_pairs = sorted(
		table.items(),
		key=lambda item: (
			-(item[1]["strength"] * item[1]["confidence"]),
			-item[1]["confidence"],
			item[0],
		),
	)
	print("Candidate count:", len(candidates))
	print("Exhaustive pair count:", len(table))
	print("Pairs sorted by score (strength * confidence):")
	for rank, (pair, score) in enumerate(sorted_pairs, start=1):
		ranking_score = score["strength"] * score["confidence"]
		print(f"\nRank {rank}")
		print("  Pair:", pair)
		print(f"  Score: {ranking_score:.3f}")
		print(f"  Strength: {score['strength']:.3f}")
		print(f"  Confidence: {score['confidence']:.3f}")
		print("  Count:", score["n"])
		print("  Containing candidates:", score["containing_candidates"])