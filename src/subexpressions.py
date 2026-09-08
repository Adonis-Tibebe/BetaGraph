"""Canonicalize and extract sub-expressions from nested Boolean tuples."""


def canon(node):
	"""Return a canonical string representation of a Boolean expression."""
	if isinstance(node, str):
		return node

	operator = node[0]
	if operator == "NOT":
		return f"NOT({canon(node[1])})"

	left, right = sorted((canon(node[1]), canon(node[2])))
	return f"({left} {operator} {right})"


def all_subexpressions(node, expressions=None):
	"""Collect every canonical sub-expression in a nested tuple tree."""
	if expressions is None:
		expressions = set()

	expressions.add(canon(node))
	if not isinstance(node, str):
		for child in node[1:]:
			all_subexpressions(child, expressions)
	return expressions


if __name__ == "__main__":
	expression = ("AND", "A", ("OR", "C", "B"))
	print("Expression:", expression)
	print("Canonical form:", canon(expression))
	print("Sub-expressions:")
	for subexpression in sorted(all_subexpressions(expression)):
		print("-", subexpression)