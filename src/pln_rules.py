"""Graph-native PLN-inspired rules for candidate and pair beliefs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class STV:
	"""A PLN simple truth value: strength and confidence."""

	strength: float
	confidence: float


def _clamp(value):
	return max(0.0, min(1.0, value))


def _as_stv(value):
	if isinstance(value, STV):
		return value
	return STV(float(value[0]), float(value[1]))


def _truth_c2w(confidence):
	denominator = 1.0 - confidence
	return confidence / denominator if denominator else 0.0


def _truth_w2c(weight):
	denominator = weight + 1.0
	return weight / denominator if denominator else 0.0


def deduction(source_stv, factor_stv):
	"""Pass a belief through a deterministic containment factor.

	This is the local factor-graph rule for containment edges. A deterministic
	containment factor ``STV(1, 1)`` passes the source belief through unchanged.
	"""
	source, factor = map(_as_stv, (source_stv, factor_stv))
	strength = source.strength * factor.strength
	confidence = min(source.confidence, factor.confidence)
	return STV(_clamp(strength), _clamp(confidence))


def induction(source_candidate_stv, shared_pair_stv):
	"""Create a candidate message through a shared pair.

	This is a graph-native PLN-inspired heuristic, not PeTTa's five-STV
	formula. The source candidate and shared pair are independent evidence
	paths, so their strengths are multiplied and the weaker confidence is kept.
	"""
	source_candidate, shared_pair = map(
		_as_stv, (source_candidate_stv, shared_pair_stv)
	)
	strength = source_candidate.strength * shared_pair.strength
	confidence = min(source_candidate.confidence, shared_pair.confidence)
	return STV(_clamp(strength), _clamp(confidence))


def abduction(source_pair_stv, shared_candidate_stv):
	"""Create a pair message through a shared candidate.

	This is the graph-native PLN-inspired counterpart to PeTTa Abduction.
	It uses the source pair and shared candidate as the two evidence paths;
	the propagation layer computes the reverse direction separately.
	"""
	source_pair, shared_candidate = map(
		_as_stv, (source_pair_stv, shared_candidate_stv)
	)
	strength = source_pair.strength * shared_candidate.strength
	confidence = min(source_pair.confidence, shared_candidate.confidence)
	return STV(_clamp(strength), _clamp(confidence))


def revision(stv_1, stv_2):
	"""Pool two estimates of the same node belief."""
	first, second = map(_as_stv, (stv_1, stv_2))
	weight_1 = _truth_c2w(first.confidence)
	weight_2 = _truth_c2w(second.confidence)
	total_weight = weight_1 + weight_2
	if total_weight == 0.0:
		return STV(0.5, 0.0)

	strength = (weight_1 * first.strength + weight_2 * second.strength) / total_weight
	confidence = max(_truth_w2c(total_weight), first.confidence, second.confidence)
	return STV(_clamp(strength), _clamp(confidence))


if __name__ == "__main__":
	candidate = STV(0.7, 0.8)
	shared_pair = STV(0.6, 0.7)
	pair = STV(0.5, 0.75)
	containment = STV(1.0, 1.0)

	print("Deduction message:", deduction(pair, containment))
	print("Induction message:", induction(candidate, shared_pair))
	print("Abduction message:", abduction(pair, candidate))
	print("Revision:", revision(candidate, shared_pair))