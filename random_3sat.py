import random
import time
import statistics

def random_3sat_instance(N, K, L):
    propositions = list(range(1, N + 1))
    clauses = []

    for _ in range(L):
        clause = random.sample(propositions, K)
        clause = [lit if random.choice([True, False]) else -lit for lit in clause]
        clauses.append(clause)

    return clauses

def find_2_clause_variable(cnf_formula):
    two_clause_count = {}
    for clause in cnf_formula:
        if len(clause) == 2:
            for var in clause:
                var_abs = abs(var)
                two_clause_count[var_abs] = two_clause_count.get(var_abs, 0) + 1

    # Return the variable that appears most frequently in 2-clauses
    if two_clause_count:
        return max(two_clause_count, key=two_clause_count.get)
    return None


def find_random_variable(cnf_formula):
    literals = [literal for clause in cnf_formula for literal in clause]
    return abs(random.choice(literals)) if literals else None

def dpil_heuristic(cnf_formula):
    literal_count = {}
    for clause in cnf_formula:
        for literal in clause:
            literal_count[literal] = literal_count.get(literal, 0) + 1
    return max(literal_count, key=literal_count.get) if literal_count else None

def update_formula(clauses, variable):
    new_clauses = []
    for clause in clauses:
        new_clause = set(clause)
        if variable in new_clause:
            new_clause.remove(variable)
        if -variable in new_clause:
            new_clause.remove(-variable)
        if len(new_clause) > 0:
            new_clauses.append(new_clause)
    return new_clauses

def dpll_satisfiable(cnf_formula, N, heuristic):
    def unit_propagate(clauses, assignments):
        changed = True
        while changed:
            changed = False
            new_clauses = []
            for clause in clauses:
                if len(clause) == 1:
                    unit_literal = next(iter(clause))
                    if unit_literal in assignments:
                        # If the unit clause's literal is already assigned correctly, we continue.
                        if assignments[unit_literal] is True:
                            continue
                        else:
                            # Conflict, as the assignment contradicts the unit clause.
                            return [], assignments
                    elif -unit_literal in assignments:
                        # If the negation is assigned True, this clause is satisfied and we skip it.
                        continue
                    else:
                        # Assign the unit clause's literal as True and mark as changed.
                        assignments[unit_literal] = True
                        changed = True
                else:
                    new_clauses.append(clause)

            if changed:
                # If there was a change, we update the clauses list based on the new assignments.
                clauses = [clause for clause in new_clauses if not any(lit in assignments and assignments[lit] for lit in clause)]
                clauses = [{lit for lit in clause if -lit not in assignments} for clause in clauses]

            return clauses, assignments


    def is_satisfied(clauses):
        return all(len(clause) == 0 for clause in clauses)

    def is_conflict(clauses):
        return any(len(clause) == 0 for clause in clauses)

    def select_unassigned_variable(assignments, N):
        for i in range(1, N + 1):
            if i not in assignments and -i not in assignments:
                return i
        return None

    num_calls = 0
    assignments = {}
    clauses, assignments = unit_propagate(cnf_formula, assignments)
    stack = [(clauses, assignments)]
    split_count = 0
    while stack:

        num_calls += 1
        clauses, assignments = stack.pop()

        if is_conflict(clauses):
            continue
        # Example return statement when a satisfying assignment is found
        if is_satisfied(clauses):
            return True, num_calls, split_count

        variable = heuristic(clauses) if heuristic else select_unassigned_variable(assignments, N)
        if variable is None:
            continue  # No more variables to assign, but not satisfied
        split_count += 1  # Increment the split count here

        # Try assigning the variable to True
        new_assignments = assignments.copy()
        new_assignments[variable] = True
        new_clauses, new_assignments = unit_propagate(update_formula(clauses, variable), new_assignments)
        stack.append((new_clauses, new_assignments))

        # Try assigning the variable to False
        new_assignments = assignments.copy()
        new_assignments[-variable] = False
        new_clauses, new_assignments = unit_propagate(update_formula(clauses, -variable), new_assignments)
        stack.append((new_clauses, new_assignments))

    return False, num_calls, split_count  # If the stack is empty, the formula is unsatisfiable

def run_experiment(N, L, heuristic):
    cnf_formula = random_3sat_instance(N, 3, L)
    start_time = time.time()
    satisfiable, num_calls, split_count = dpll_satisfiable(cnf_formula, N, heuristic)  # Updated to include split count
    compute_time = time.time() - start_time
    return satisfiable, compute_time, num_calls, split_count

def evaluate_performance(N, heuristic, increment=0.2, start_ratio=3, end_ratio=6, num_experiments=100):
    results = []
    for ratio in [start_ratio + i * increment for i in range(int((end_ratio - start_ratio) / increment) + 1)]:
        L = int(ratio * N)
        experiment_results = [run_experiment(N, L, heuristic) for _ in range(num_experiments)]
        satisfiable_results = [result for result in experiment_results if result[0]]
        split_counts = [result[3] for result in experiment_results]  # Collect split counts
        median_splits = statistics.median(split_counts) if split_counts else 0
        median_compute_time = statistics.median([result[1] for result in experiment_results])
        satisfiability_probability = len(satisfiable_results) / num_experiments
        results.append((ratio, median_compute_time, satisfiability_probability, median_splits))
    return results


if __name__ == "__main__":
    N_values = [100, 125]
    heuristics = [find_random_variable, find_2_clause_variable, dpil_heuristic]

    for N in N_values:
        for heuristic in heuristics:
            performance_results = evaluate_performance(N, heuristic)
            for ratio, median_time, probability, median_splits in performance_results:
                print(f"N={N}, L/N={ratio}, Heuristic={heuristic.__name__}, "
                      f"Median Time={median_time}, Probability={probability}, "
                      f"Median Splits={median_splits}")
