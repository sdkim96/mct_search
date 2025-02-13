import argparse
from dotenv import load_dotenv
from app.tree import MonteCarloTree

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run MonteCarloTree with a query.")
    parser.add_argument("query", type=str, help="The query to process")
    args = parser.parse_args()

    tree = MonteCarloTree(
        leafs_limit=3,
        depth_limit=3,
        snapshot=True
    )
    solution = tree.run(args.query, loop=3, pre_terminate=True)

    if solution:
        print(solution.model_dump(mode='json'))
    else:
        print("No solution found")

if __name__ == "__main__":
    main()