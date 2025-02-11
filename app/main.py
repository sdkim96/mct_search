
def main():
    from dotenv import load_dotenv
    from tree import MonteCarloTree
    load_dotenv()

    query = "Who was the president of Korea that has bald hair?"

    tree = MonteCarloTree(snapshot=True)
    solution = tree.run(query=query, loop=3, pre_terminate=True)

    print(solution)


if __name__ == "__main__":
    main()
    