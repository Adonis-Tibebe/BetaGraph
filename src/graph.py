"""Build the candidate/pair factor graph used by propagation."""

import sys
from pathlib import Path

if __package__ in {None, ""}:
	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pln_rules import STV
from src.subexpressions import all_subexpressions


class VariableNode:
	"""A candidate or pair variable with its current belief."""

	def __init__(self, kind, identifier, belief, data=None):
		self.kind = kind
		self.identifier = identifier
		self.belief = belief
		self.data = {} if data is None else data


class FactorNode:
	"""A local PLN function and the variables in its scope."""

	def __init__(self, rule, variables, belief=None):
		self.rule = rule
		self.variables = variables
		self.belief = belief


class FactorGraph:
	"""Variable and factor nodes plus indexes used by propagation."""

	def __init__(self):
		self.variable_nodes = {}
		self.factor_nodes = []
		self.candidates_sharing_pair = {}
		self.pairs_sharing_candidate = {}

	@property
	def candidate_nodes(self):
		return {
			identifier: node
			for (kind, identifier), node in self.variable_nodes.items()
			if kind == "candidate"
		}

	@property
	def pair_nodes(self):
		return {
			identifier: node
			for (kind, identifier), node in self.variable_nodes.items()
			if kind == "pair"
		}

	@property
	def containment_factors(self):
		return [factor for factor in self.factor_nodes if factor.rule == "deduction"]


def build_graph(candidate_data, candidate_evidence, selected_pairs):
	"""Build a class-based bipartite graph from selected pair nodes.

	Candidate and pair variables hold current beliefs. Factors store the local
	Deduction, Induction, or Abduction function and its variable scope.
	"""
	graph = FactorGraph()

	for candidate_id, tree in candidate_data.items():
		graph.variable_nodes[("candidate", candidate_id)] = VariableNode(
			kind="candidate",
			identifier=candidate_id,
			belief=STV(
				candidate_evidence[candidate_id]["strength"],
				candidate_evidence[candidate_id]["confidence"],
			),
			data={"tree": tree},
		)

	for pair, metrics in selected_pairs.items():
		graph.variable_nodes[("pair", pair)] = VariableNode(
			kind="pair",
			identifier=pair,
			belief=STV(metrics["strength"], metrics["confidence"]),
			data={"metrics": metrics},
		)

	candidate_to_pairs = {candidate_id: [] for candidate_id in candidate_data}
	pair_to_candidates = {pair: [] for pair in selected_pairs}

	for candidate_id, tree in candidate_data.items():
		expressions = all_subexpressions(tree)
		for pair in selected_pairs:
			if pair[0] not in expressions or pair[1] not in expressions:
				continue

			graph.factor_nodes.append(
				FactorNode(
					rule="deduction",
					variables=(
						("pair", pair),
						("candidate", candidate_id),
					),
					belief=STV(1.0, 1.0),
				)
			)
			candidate_to_pairs[candidate_id].append(pair)
			pair_to_candidates[pair].append(candidate_id)

	graph.candidates_sharing_pair = {
		pair: tuple(candidate_ids)
		for pair, candidate_ids in pair_to_candidates.items()
	}
	graph.pairs_sharing_candidate = {
		candidate_id: tuple(pairs)
		for candidate_id, pairs in candidate_to_pairs.items()
	}

	for pair, candidate_ids in graph.candidates_sharing_pair.items():
		if len(candidate_ids) < 2:
			continue
		graph.factor_nodes.append(
			FactorNode(
				rule="induction",
				variables=(
					("pair", pair),
					*(
						("candidate", candidate_id)
						for candidate_id in candidate_ids
					),
				),
			)
		)

	for candidate_id, pairs in graph.pairs_sharing_candidate.items():
		if len(pairs) < 2:
			continue
		graph.factor_nodes.append(
			FactorNode(
				rule="abduction",
				variables=(
					("candidate", candidate_id),
					*(
						("pair", pair)
						for pair in pairs
					),
				),
			)
		)

	return graph


if __name__ == "__main__":
	from data.candidates import candidates, rows, target
	from src.cooccurrence import score_all_pairs
	from src.parsing import evaluate_candidates
	from src.selection import select_top_pairs

	evidence = evaluate_candidates(candidates, rows, target)
	all_pairs = score_all_pairs(candidates, evidence)
	selected_pairs = select_top_pairs(all_pairs, len(candidates))
	graph = build_graph(candidates, evidence, selected_pairs)

	print("Candidate nodes:", len(graph.candidate_nodes))
	print("Pair nodes:", len(graph.pair_nodes))
	print("Deduction factors:", len(graph.containment_factors))
	print("Induction factors:", sum(factor.rule == "induction" for factor in graph.factor_nodes))
	print("Abduction factors:", sum(factor.rule == "abduction" for factor in graph.factor_nodes))
	print("Candidates sharing first pair:", next(iter(graph.candidates_sharing_pair.items())))
	print("Pairs sharing candidate 1:", graph.pairs_sharing_candidate[1])