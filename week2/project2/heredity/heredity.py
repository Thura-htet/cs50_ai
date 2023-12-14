import csv
import itertools
import sys
from math import prod
PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    queries = generate_qs(people, one_gene, two_genes, have_trait)
    probabilities = []
    for person in people:
        if not is_child(person, people):
            gene = PROBS["gene"][queries[person]["gene"]]
            trait = PROBS["trait"][queries[person]["gene"]][queries[person]["trait"]]
            probability = gene * trait
            probabilities.append(probability)
        else:
            child_num_gene = queries[person]['gene']
            father = people[person]['father']
            mother = people[person]['mother']
            if child_num_gene == 0:
                not_from_father = p_inherit(queries[father]['gene'], False) 
                not_from_mother = p_inherit(queries[mother]['gene'], False)
                gene = not_from_father * not_from_mother
            elif child_num_gene == 1:
                not_from_father = p_inherit(queries[father]['gene'], False) 
                not_from_mother = p_inherit(queries[mother]['gene'], False)
                from_father = p_inherit(queries[father]['gene'], True)
                from_mother = p_inherit(queries[mother]['gene'], True)
                gene = (not_from_father * from_mother) + (from_father * not_from_mother)
            else:
                from_father = p_inherit(queries[father]['gene'], True)
                from_mother = p_inherit(queries[mother]['gene'], True)
                gene = from_father * from_mother
            trait = PROBS["trait"][queries[person]["gene"]][queries[person]["trait"]]
            probability = gene * trait
            probabilities.append(probability)
    return prod(probabilities)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    queries = generate_qs(probabilities, one_gene, two_genes, have_trait)
    for person in probabilities:
        probabilities[person]['gene'][queries[person]["gene"]] += p
        probabilities[person]['trait'][queries[person]['trait']] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        genes = probabilities[person]['gene']
        traits = probabilities[person]['trait']
        sum_genes = sum(genes.values())
        sum_traits = sum(traits.values())
        for gene in genes:
            genes[gene] = genes[gene] / sum_genes
        for trait in traits:
            traits[trait] = traits[trait] / sum_traits

def is_child(person, people):
    return (people[person]['father'] is not None) and (people[person]['mother'] is not None)

def person_gene(person, one_gene, two_genes):
    if person in one_gene:
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0

def person_trait(person, have_trait):
    if person in have_trait:
        return True
    else:
        return False

def p_inherit(num_genes, from_parent):
    if num_genes == 1:
        return 0.5
    passed = num_genes / 2
    return PROBS['mutation'] if passed != from_parent  else (1 - PROBS['mutation'])

def generate_qs(people, one_gene, two_genes, have_trait):
    return {
        person: {
            'gene': person_gene(person, one_gene, two_genes),
            'trait': person_trait(person, have_trait)
        }
        for person in people
    }

if __name__ == "__main__":
    main()
