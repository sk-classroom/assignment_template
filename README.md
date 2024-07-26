Read the Task section and generate the results. Then, submit the results by PR, which will run autograding by GitHub for a quick feedback. Note that this exercise is not grading item.

# Exercise
- See `notebooks` folder.

# Task

## Starter : Find Erdos Number

The Erdős Number is the minimum number of connections between an individual and Paul Erdős in the collaboration network of scientists. Scientists often take great pride in having a low Erdos Number 🙂.

In this task, we will compute the Erdős Number by using [SciSciNet](https://www.google.com/search?q=scisci+datalake). Since the SciSciNet is a big data, we work with a subset of the dataset, which consists of nearly 10,000 scientists and their publications.

The data is located in the "./data" folder, and the format, including column names and IDs, has been kept consistent with the original SciSciNet. Please refer the paper for details.

Our goal is to compute the Erdős number for the scientists. We will approach the goal by the following two steps:
1. **Network construction**
2. **Computing the shortest distance from Paul Erdős**

In the first step, you will generate an edge table and a node table of the collaboration network of scientists. The collaboration network can be constructed by using a *one-mode projection* of the author-paper bipartite network, where edges represent authorships. The collaboration network is constructed by the one-mode projection because two authors are connected in the collaboration network if they are connected to the same paper in the bipartite network of authors and papers.

In the second step, you will compute the distance from Paul Erdős. You first need to identify the node ID of Paul Erdős. Then, compute the shortest distance from him to individual scientists in the network. Although you can do it with existing network analysis tools, I'd encourage you to implement it by yourself, which is the main point of this exercise.

#### Deliverables
- Produce a csv file and save it `answer-erdos-number.csv` under `answers` folder.
- The CSV should be comma separated and consists of `AuthorID`---author IDs used in SciSciNet---and `ErdosNumber` which is the Erdos Number you computed.

#### Self-evaluation
Run the following command. You will see "Successful" if the answers are correct. Otherwise, you'll get an error.

```bash
python  tests/grade.py answers/answer-erdos-number.csv tests/answer-erdos-number.csv AuthorID ErdosNumber equal
```


## Advanced: Closeness centrality

### What is the closeness centrality
Closeness centrality of a node is an average *closeness* from the node to other nodes in a network. Nodes with a high closeness are often influential on *flows* on the network such as information, goods, and disease. More specifically, a closeness of a node is defined as

$
c_i:= \frac{n-1}{\sum_{j, i\neq j} d(i,j)}
$

where $d(i,j)$ is the shortest path length between nodes $i$ and $j$, and $n$ is the number of nodes in the network.
Let's calculate the closeness centrality for all scientists, and see who is the most influential. You may use the [scipy.sparse.csgraph.shortest_path](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csgraph.shortest_path.html).

#### Deliverables
- Produce a csv file and save it `answer-closeness-centrality.csv` under `answers` folder.
- The CSV should be comma separated and consists of `AuthorID`---author IDs used in SciSciNet---and `Centrality` which is the closeness centrality you computed.

#### Self-evaluation
Run the following command. You will see "Successful" if the answers are correct. Otherwise, you'll get an error.

```bash
python  tests/grade.py answers/answer-closeness-centrality.csv tests/answer-closeness-centrality.csv AuthorID Centrality isclose
```

## Expert: PageRank

PageRank is an algorithm used by search engines to rank web pages based on their importance. It was developed by Larry Page and Sergey Brin, the co-founders of Google, while they were Ph.D. students at Stanford University. PageRank revolutionized the way search engines ranked web pages and played a crucial role in the success of Google. We will implement the PageRank algorithm and learn its theoretical foundations.

The main concept behind PageRank is quite straightforward. It involves simulating the way we navigate through web pages and keeping track of how often each webpage is visited.
1. PageRank is based on a simulation of an agent who explores the network of web pages.
2. The agent begins by selecting a webpage at random.
3. From the chosen webpage, the agent randomly selects a link and moves to another webpage through that link.
4. In the event that the agent encounters a dangling webpage (one without any external links) or with a small probability $\alpha$, the agent is *teleported* to a randomly chosen webpage and goes back to step 2.
5. Repeat the rounds of steps 2 and 4 for a prescribed number of steps.

Here is the outline of the algorithm:
```python
def PageRank(A, n_steps = 100000, teleportation_prob = 0.25):
    """PageRank algrithm
    A: scipy sparse csr matrix
    n_steps: number of walks. Defaults to  1000
    teleportation_prob: Probability of teleportation, defaults to 0.25.
    """
    n_nodes = A.shape[0] # number of nodes
    pr = np.zeros(n_nodes) # This records te number of times a walker visist each node.
    current_node = np.random.randint(0, n_nodes) # start from a randomly selected web page
    for n in range(n_steps):
        pr[current_node]+=1 # Inclement the counter by 1 at current_node.

        # Your code -------
        # Find the neighbors of the node `current_node`. You can exploit the property of the CSR matrix such as indices and indptr to do this.
        # Check out the previous module on data representation.
        neighbors = ...


    return pr/np.sum(pr) # normalization
```

#### Deliverables
- Produce a csv file and save it `answer-pagerank.csv` under `answers` folder.
- The CSV should be comma separated and consists of `AuthorID`---author IDs used in SciSciNet---and `PageRank` which is the PageRank scores you computed.

#### Self-evaluation
Run the following command. You will see "Successful" if the answers are correct. Otherwise, you'll get an error.

```bash
python  tests/grade.py answers/answer-pagerank.csv tests/answer-pagerank.csv AuthorID PageRank correlation
```