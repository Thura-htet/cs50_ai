import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probablity_distribution = {}

    linked_pages = corpus[page]
    all_pages = get_all_pages(corpus)

    random_chosen = (1.0 - damping_factor) / len(all_pages)
    for element in all_pages:
        probablity_distribution[element] = random_chosen

    if len(linked_pages) == 0:
        random_linked = damping_factor / len(all_pages)
        for element in all_pages:
            probablity_distribution[element] += random_linked
    else:
        random_linked = damping_factor / len(linked_pages)
        for element in linked_pages:
            probablity_distribution[element] += random_linked

    return probablity_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = get_all_pages(corpus)
    sample = random.sample(all_pages, 1)[0]
    pagerank = {sample: 1/n}
    for i in range(1, n):
        probability_distribution = transition_model(corpus, sample, damping_factor)
        sample = random.choices(list(probability_distribution.keys()), list(probability_distribution.values()))[0]
        if sample in pagerank:
            pagerank[sample] += 1/n
        else:
            pagerank[sample] = 1/n
    return pagerank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = get_all_pages(corpus)

    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = all_pages

    N = len(all_pages)
    C = (1 - damping_factor) / N
    pagerank = {}
    prev_pagerank = {}
    for page in all_pages:
        pagerank[page] = 1 / N
        prev_pagerank[page] = 1 / N
    
    while True:
        prev_pagerank = copy.deepcopy(pagerank)
        for page in all_pages:
            incoming_links = get_incoming_links(corpus, page, N)
            pagerank[page] = C + (damping_factor * sum([prev_pagerank[key] / value for key, value in incoming_links.items()]))
        if all([abs(pagerank[page]-prev_pagerank[page] < 0.001) for page in all_pages]): 
            return pagerank

def get_all_pages(corpus):
    all_pages = list(corpus)
    for key in corpus:
        for element in corpus[key]:
            if element not in all_pages:
                all_pages.append(element)
    return all_pages

def get_incoming_links(corpus, page, N):
    incoming_links = {}
    for key in corpus:
        if page in corpus[key]:
            incoming_links[key] = len(corpus[key])
    return incoming_links


if __name__ == "__main__":
    main()
