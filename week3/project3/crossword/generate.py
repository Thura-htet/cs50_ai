import sys
from copy import deepcopy
import collections

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains = deepcopy(self.domains)

        for variable in domains:
            for value in domains[variable]:
                if len(value) != variable.length:
                    self.domains[variable].remove(value)

        # for variable, values in self.domains.items():
        #     for value in values:
        #         if len(value) != variable.length:
        #             self.domains[variable].remove(value)
                    # (or) values.remove(value)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        i, j = overlap

        revised = False
        domains = deepcopy(self.domains)

        # maybe use self.domains.keys()

        for x_value in domains[x]:
            if all(x_value[i] != y_value[j] for y_value in domains[y]):
                if x_value in self.domains[x]:
                    self.domains[x].remove(x_value)
                    revised = True
        
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = list(self.crossword.overlaps.keys())
        
        while arcs:
            arc = arcs.pop(0)
            x, y = arc
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                neighbors = self.crossword.neighbors(x)
                neighbors.remove(y)
                if neighbors is not None:
                    for z in neighbors:
                        arcs.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all((variable in assignment and assignment[variable] != None) for variable in self.domains)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        unary = False
        binary = False

        if assignment is None or len(assignment.values()) != len(set(assignment.values())):
            return False

        for variable in assignment:

            if (assignment[variable] == None):
                continue

            unary = len(assignment[variable]) == variable.length
            if not unary:
                return False

            neighbors = self.crossword.neighbors(variable)
            for neighbor in neighbors:
                if neighbor in assignment:
                    v, n = self.crossword.overlaps[variable, neighbor]
                    if assignment[variable][v] != assignment[neighbor][n]:
                        return False
            binary = True

        return unary and binary


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var) - set(assignment.keys())
        values_counts = {}

        v_values = self.domains[var]
        for v_value in v_values:
            count = 0
            for neighbor in neighbors:
                n_values = self.domains[neighbor]
                if v_value not in n_values:
                    continue
                v, n = self.crossword.overlaps[var, neighbor]
                for n_value in n_values:
                    if v_value[v] != n_value[n]:
                        count += 1
            values_counts[v_value] = count

        # values_count = collections.defaultdic(list)
        
        return sorted(values_counts, key=lambda value: values_counts[value])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_variables = set(self.domains.keys()) - set(assignment.keys())

        domains_variables = {}
        for variable in unassigned_variables:
            num_remains = len(self.domains[variable])
            if num_remains in domains_variables:
                domains_variables[num_remains].append(variable)
            else:
                domains_variables[num_remains] = [variable]

        min_key = min(domains_variables)
        if len(domains_variables[min_key]) == 1:
            return domains_variables[min_key][0]

        tie_variables = domains_variables[min_key]
        return max(tie_variables, key=lambda variable: len(self.crossword.neighbors(variable)))
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)
        domain_values = self.order_domain_values(variable, assignment)

        for value in domain_values:
            assignment.update({ variable: value })
            if self.consistent(assignment):
                neighbors = self.crossword.neighbors(variable)
                arcs = [(neighbor, variable) for neighbor in neighbors]
                if self.ac3(arcs=arcs):
                    for neighbor in neighbors:
                        if (len(self.domains[neighbor]) == 1) and (neighbor not in assignment):
                            assignment.update({ neighbor: list(self.domains[neighbor])[0] })

                result = self.backtrack(assignment)
                if result != None:
                    return result
                assignment.pop(variable)
            else:
                assignment.pop(variable)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
