import itertools
import math
import re
import sys


def debug(message):
    print(message, file=sys.stderr, flush=True)


def eval_equation(equation):
    debug("eval_equation")
    debug("equation")
    debug(equation)
    unique_letters = list(set(extract_letters(equation)))
    debug(unique_letters)

    def generalized_loop(ranges):
        combos = []
        # Create a cartesian product based on the provided ranges
        for combination in itertools.product(*ranges):
            # Do something with the combination
            # print(combination)
            combos.append(combination)
        return combos

    # Example usage with 3 ranges like in your example
    ranges = [range(1, 3) for _ in unique_letters]
    options = generalized_loop(ranges)

    sols = []
    for option in options:
        # debug("option")
        # debug(option)
        eval_str = equation
        for index, letter in enumerate(unique_letters):
            # debug("index")
            # debug(index)
            # debug("letter")
            # debug(letter)
            eval_str = eval_str.replace(letter, str(option[index]))
        # debug(eval_str)

        res = eval(eval_str)
        if res == 0:
            sols.append(option)

    return sols


def get_common_items_sorted(*arrays):
    # Convert the inner arrays of each argument to tuples and create sets for each array
    sets_of_arrays = [{tuple(item) for item in arr} for arr in arrays]
    debug("sets_of_arrays")
    debug(sets_of_arrays)

    # Find the common items by intersecting all the sets
    common_items = set.intersection(*sets_of_arrays)
    debug("common_items")
    debug(common_items)

    # Convert the tuples back to lists
    common_items = [list(item) for item in common_items]
    debug("common_items")
    debug(common_items)

    # Sort by the sum of the elements in each array
    common_items.sort(key=lambda x: sum(x))

    return common_items


def split_to_dict(expression):
    # Use re.findall to match a letter followed by an optional number
    matches = re.findall(r"([A-Z])(\d*)", expression)
    # Convert the list of tuples to a dictionary, assigning 1 if no number is found
    result_dict = {letter: int(number) if number else 1 for letter, number in matches}
    return result_dict

def split_by_parts(expression):
    terms = {}
    for term in re.split(r"([A-Z])(\d*)", expression):
        term = term.strip()
        terms[term] = split_to_dict(term)
    return terms


def split_by_term(expression):
    terms = {}
    for term in re.split(r"(\+|\-)", expression):
        term = term.strip()
        terms[term] = split_to_dict(term)
    return terms


def extract_letters(string):
    result = ""
    for char in string:
        if char.isalpha():
            result += char
    return result


unbalanced = input()
debug(unbalanced)

equations = {}
solutions = {}
unique_letters = set(extract_letters(unbalanced))
debug(unique_letters)
unique_letter_mapping = {unique_letter: None for unique_letter in unique_letters}
debug(unique_letter_mapping)
rhs = unbalanced.split(" -> ")[1]
lhs = unbalanced.split(" -> ")[0]

debug("rhs")
debug(rhs)
rhs_terms = split_by_term(rhs)
debug("rhs_terms")
debug(rhs_terms)

debug("lhs")
debug(lhs)
lhs_terms = split_by_term(lhs)
debug("lhs_terms")
debug(lhs_terms)

debug("creating equation...")
unique_letters_for_equations = ["a", "b", "c", "d", "e", "f", "g"]
for unique_letter in unique_letters:
    unique_letter_id = 0
    debug("unique_letter")
    debug(unique_letter)
    eq_parts = []
    debug("DOING LHS")
    for key, letters in lhs_terms.items():
        # debug("key")
        # debug(key)
        # debug("letters")
        # debug(letters)
        if key in ["+", "-"]:
            eq_parts.append(key)
        else:
            eq_parts.append(
                f"{unique_letters_for_equations[unique_letter_id]} * {letters.get(unique_letter, 0)}"
            )
            unique_letter_id += 1

    eq_parts.append("-")
    debug("DOING RHS")
    for key, letters in rhs_terms.items():
        # debug("key")
        # debug(key)
        # debug("letters")
        # debug(letters)
        if key in ["+"]:
            eq_parts.append("-")
        elif key in "-":
            eq_parts.append("+")
        else:
            eq_parts.append(
                f"{unique_letters_for_equations[unique_letter_id]} * {letters.get(unique_letter, 0)}"
            )
            unique_letter_id += 1

    # debug("eq_parts")
    # debug(eq_parts)
    equations[unique_letter] = " ".join(eq_parts)

# debug("equations")
# debug(equations)


for equation in equations.values():
    solutions[equation] = eval_equation(equation)

debug("solutions")
debug(solutions)

# all_sols = []
# for sols in solutions.values():
#     all_sols.extend(sols)

# all_solutions = [sols for sols in solutions.values()]
# debug(all_sols)

common_sols = get_common_items_sorted(*list(solutions.values()))
debug(common_sols)
sol = common_sols[0] if len(common_sols) else None

# turn back to the equation
if not sol:
    print(None)

debug("sol")
debug(sol)
result_parts = []
i = 0
for grouping in lhs_terms.keys():
    debug("grouping")
    debug(grouping)
    if grouping in ["+", "-"]:
        result_parts.append(grouping)
    else:
        result_parts.append(f"{sol[i]}{grouping}")
        i += 1
result_parts.append("->")
for grouping in rhs_terms.keys():
    debug("grouping")
    debug(grouping)
    if grouping in ["+", "-"]:
        result_parts.append(grouping)
    else:
        result_parts.append(f"{sol[i]}{grouping}")
        i += 1
print(" ".join(result_parts))