
def dpll_satisfiable(cnf_formula):
    def propagate_unit_clauses(clauses, assignments):
        while any(len(clause) == 1 for clause in clauses):
            unit_clause = next(iter(clause) for clause in clauses if len(clause) == 1)
            unit_literal = next(iter(unit_clause))
            if -unit_literal in assignments:
                return None  # Conflict found
            assignments[unit_literal] = True
            clauses = [c for c in clauses if unit_literal not in c]
            clauses = [{literal for literal in clause if -literal != unit_literal} for clause in clauses]
        return clauses
    def most_frequent_variable(cnf_formula):
        variable_counts = {}
        for clause in cnf_formula:
            for literal in clause:
                var = abs(literal)
                variable_counts[var] = variable_counts.get(var, 0) + 1
        return max(variable_counts, key=variable_counts.get)

    assignments = {}
    stack = [(cnf_formula, assignments)]
    while stack:
        clauses, current_assignments = stack.pop()

        # Unit propagation
        propagated = propagate_unit_clauses(clauses, current_assignments)
        if propagated is None:
            continue  # Conflict, backtrack
        else:
            clauses = propagated

        # Check for satisfaction
        if not clauses:
            return [var if val else -var for var, val in current_assignments.items()]  # Satisfying assignment found

        # Choose literal for branching
        literal = next(iter(next(iter(clause)) for clause in clauses if next(iter(clause)) not in current_assignments))

        # Branch with the literal set to True
        true_assignments = current_assignments.copy()
        true_assignments[literal] = True
        stack.append(([c for c in clauses if literal not in c], true_assignments))

        # Branch with the literal set to False
        if -literal not in current_assignments:
            false_assignments = current_assignments.copy()
            false_assignments[-literal] = False
            stack.append(([c for c in clauses if -literal not in c], false_assignments))

    return None  # No satisfying assignment found



if __name__ == '__main__':
    with open('einstein.cnf', 'r') as f:
        cnf_content = f.read().splitlines()

    cnf_formula = [list(map(int, line.split()[:-1])) for line in cnf_content if line and line[0] not in ('c', 'p')]

    result = dpll_satisfiable(cnf_formula)

    if result is not None:
        print("Satisfying assignment found:")
        print(' '.join(map(str, result)))  # Print the variables with their assigned values
    else:
        print("No satisfying assignment found.")