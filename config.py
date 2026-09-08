"""Configuration values for the factor-graph PLN experiment."""

# PLN confidence constant used when converting evidence counts to confidence.
PLN_K = 1.0

# Minimum number of containing candidates required for a pair to be considered.
N_MIN = 2

# Number of ranked pair nodes retained after exhaustive pair scoring.
TOP_K = 10

# Maximum belief change allowed before propagation is considered stable.
CONVERGENCE_THRESHOLD = 1e-6