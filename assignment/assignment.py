import marimo

__generated_with = "0.14.16"
app = marimo.App(width="full", theme="dark")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Small-World Networks Assignment

    Welcome to <PLACEHOLDER> assignment!

    Briefly describe the assignment here.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # 📋 Assignment Instructions & Grading
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.accordion(
        {
            "📋 Assignment Tasks": mo.md(
                r"""
            Complete the following tasks and upload your notebook to your GitHub repository.

            1. **Task 1**: Describe the assignment task
            2. **Task 2**: Describe the assignment task
            3. **Task 3**: Describe the assignment task
            4. Update this notebook by using `git add`, `git commit`, and then `git push`.
            5. The notebook will be automatically graded, and your score will be shown on GitHub.
            """
            ),
            "🔒 Protected Files": mo.md(
                r"""
            Protected files are test files and configuration files you cannot modify. They appear in your repository but don't make any changes to them.
            """
            ),
            "⚖️ Academic Integrity": mo.md(
                r"""
            There is a system that automatically checks code similarity across all submissions and online repositories. Sharing code or submitting copied work will result in zero credit and disciplinary action.

            While you can discuss concepts, each student must write their own code. Cite any external resources, including AI tools, in your comments.
            """
            ),
            "📚 Allowed Libraries": mo.md(
                r"""
            You **cannot** import any other libraries that result in the grading script failing or a zero score. Only use: <PLACEHOLDER>
            """
            ),
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Task 1: Describe the assignment task

    Describe the assignment task here.
    """
    )
    return


@app.function
# Task 1
def compute_global_clustering(g):
    """
    Compute the global clustering coefficient of a graph.

    Args:
        g (igraph.Graph): Input graph

    Returns:
        float: Global clustering coefficient (0.0 to 1.0)
    """
    pass


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Task 2: Average Path Length

    Describe the assignment task here.
    """
    )
    return


@app.function
# Task 2
def compute_average_path_length(g):
    """
    Compute the average shortest path length of a graph.

    Args:
        g (igraph.Graph): Input graph (should be connected)

    Returns:
        float: Average path length
    """
    pass


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Task 3: Small-World Coefficient

    Describe the assignment task here.

    Describe the assignment task here.
    """
    )
    return


@app.function
# Task 3
def compute_small_world_coefficient(g):
    """
    Compute the small-world coefficient using random graph as reference.

    Args:
        g (igraph.Graph): Input graph

    Returns:
        float: Small-world coefficient (σ)
    """
    pass


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    ## Interactive Visualization

    Put the visualization to test the students' implementation here.
    """
    )
    return



@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Understanding the Visualization

    Reflect on the visualization and the assignment task.

    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Libraries""")
    return


@app.cell
def _():
    # All imports in one place to avoid conflicts
    import numpy as np
    import igraph
    import altair as alt
    import pandas as pd
    return alt, igraph, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Code""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#### ...""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#### Filter Data""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""#### Create Visualization""")
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
