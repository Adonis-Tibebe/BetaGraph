"""Filter and select pair nodes from the exhaustive co-occurrence table."""

import sys
from pathlib import Path

if __package__ in {None, ""}:
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import N_MIN, TOP_K


def benchmark_score(metrics):
	"""Score how informative and well-supported a pair is."""
	return metrics["confidence"] * abs(metrics["strength"] - 0.5)


def filter_pairs(pair_table, total_candidates, n_min=N_MIN):
	"""Keep pairs with enough support that are not present everywhere."""
	return {
		pair: metrics
		for pair, metrics in pair_table.items()
		if metrics["n"] >= n_min and metrics["n"] < total_candidates
	}


def select_top_pairs(
	pair_table,
	total_candidates,
	n_min=N_MIN,
	top_k=TOP_K,
):
	"""Filter, rank, and return the selected pair-node metrics."""
	survivors = filter_pairs(pair_table, total_candidates, n_min)
	ranked = sorted(
		survivors.items(),
		key=lambda item: (
			-benchmark_score(item[1]),
			-item[1]["confidence"],
			item[0],
		),
	)
	return {
		pair: {**metrics, "benchmark_score": benchmark_score(metrics)}
		for pair, metrics in ranked[:top_k]
	}


if __name__ == "__main__":
	from data.candidates import candidates, rows, target
	from src.cooccurrence import score_all_pairs
	from src.parsing import evaluate_candidates

	evidence = evaluate_candidates(candidates, rows, target)
	all_pairs = score_all_pairs(candidates, evidence)
	selected_pairs = select_top_pairs(all_pairs, len(candidates))

	print("Exhaustive pair count:", len(all_pairs))
	print("Pairs after filtering:", len(filter_pairs(all_pairs, len(candidates))))
	print("Selected pair count:", len(selected_pairs))
	print("Selected pair nodes:")
	for rank, (pair, metrics) in enumerate(selected_pairs.items(), start=1):
		print(f"\nRank {rank}")
		print("  Pair:", pair)
		print(f"  Benchmark score: {metrics['benchmark_score']:.3f}")
		print(f"  Strength: {metrics['strength']:.3f}")
		print(f"  Confidence: {metrics['confidence']:.3f}")
		print("  Count:", metrics["n"])
		print("  Containing candidates:", metrics["containing_candidates"])