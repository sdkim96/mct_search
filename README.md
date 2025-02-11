# 🎯 MCT Search

This repository provides a simple example of how to generate **solutions** to a given query using OpenAI Chat Completion, reflect on those solutions with **Pydantic** models, and then explore these outcomes using a **Monte Carlo Tree (MCT)**-style workflow.

---

## 🦜 QuickStart

You need `poetry` dependency to run this code.
Check Document of [Poetry](https://python-poetry.org/docs/)!

```sh
poetry install
poetry shell
python -m app.main "who is the best person in the world?"
```

Then, You can see final result dumped to json file!


## 👀 Overview

- **`models.py`**: Defines data models (using Pydantic) for:
  - **Answer**: Holds the main answer and a descriptive explanation.
  - **Solution**: Combines a query (`query`) and its answer (`Answer`).
  - **Reflection**: Holds a reflection text, a score, and a flag indicating if a valid solution was found.
  - **NodeSnapshot**, **EdgeSnapshot**, **TreeSnapshot**: Used to take "snapshots" of the tree structure (nodes, edges, solutions, reflections, etc.).

- **`chat.py`**:  
  Makes OpenAI Chat Completion API calls using an `invoke` function to parse the response into specific Pydantic models.  
  - **`solve(query, context) -> Solution`**: Generates a solution given a query and an optional context.  
  - **`reflect(solution) -> Reflection`**: Reflects on the solution to produce a reflection with a score and solution acceptance.

- **`tree.py`**:  
  Implements a **Monte Carlo Tree** to iteratively discover and refine solutions. It showcases a simplified MCTS-like process where each node can carry a `Solution` and its `Reflection`. Key steps are:
  1. **Select** a leaf node.
  2. **Expand** it by generating child solutions and reflections (`solve` + `reflect`).
  3. **Backpropagate** reflection-based scores back to the root.
  4. **Check** if a suitable solution is found or the tree depth limit is reached.

---

## 🌲 Monte Carlo Tree Search (MCT) Algorithm (Simplified)

MCTS typically involves four main phases: **Selection**, **Expansion**, **Simulation**, and **Backpropagation**. In this code, we have a streamlined approach:

1. **Selection**:  
   - We pick the best node (based on some value or heuristic) that has not been fully expanded yet.  
   - In `tree.py`, we use a simplified selection by choosing a node with the highest value among unexpanded leaves.

2. **Expansion**:  
   - Once a leaf node is chosen, it is expanded by creating child nodes.  
   - Each child node is generated by calling `chat.solve` to produce a solution, followed by `chat.reflect` to evaluate that solution.  
   - These new nodes (with their solution and reflection) get attached to the tree as children of the selected node.

3. **(Light) Simulation**:  
   - In some MCTS versions, a random simulation runs from the new node to a terminal state.  
   - Here, we do not run a separate simulation step; instead, each solution generation acts like a single-step “simulation” where the language model yields a potential answer.

4. **Backpropagation**:  
   - The reflection’s score is used to update the value of the node along the path back to the root.  
   - This helps guide future selection steps, favoring more promising branches.

By repeating these steps for a fixed number of iterations (or until a suitable solution is found), the Monte Carlo Tree can discover higher-quality solutions while pruning less promising paths.

---

## ⚙️ High-Level Execution Flow

1. **Create and Configure the Tree**  
   Instantiate `MonteCarloTree`, specifying:
   - `depth_limit`: Maximum search depth.  
   - `leafs_limit`: Number of child nodes to expand at each step.  
   - Optional snapshot settings (to record tree data).

2. **Run the Search**  
   - Call `run(query, loop, pre_terminate)`:
     - **Selection** → **Expansion** → **Backpropagation** → **Check** if solution is found or depth limit reached.  
     - Repeats up to `loop` times unless `pre_terminate=True` triggers an early exit when a valid solution is found.

3. **Obtain the Result**  
   - If a valid solution was identified, it is returned as a `Solution`.  
   - If not found within the allotted search depth or iterations, it may return `None`.

4. **(Optional) Save the Snapshot**  
   - If `snapshot=True`, the code automatically saves the tree structure as a JSON file, containing nodes, edges, and each node’s solution/reflection details.

---