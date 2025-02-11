import uuid
import random
import json
from datetime import datetime
from typing import List, Optional, Tuple

import models
import chat

ROOT_ID = uuid.UUID(int=0)
DEPTH_LIMIT = 3
LEAFS_LIMIT = 3

ROOT_REFLECTION = models.Reflection(
    reflections="Can't find the solution",
    score=1,
    found_solution=False
)

class Node:
    
    def __init__(
        self,
        reflection: models.Reflection,
        solution: models.Solution | None = None,
        parent: Optional["Node"] = None,
        id: uuid.UUID = uuid.uuid4()   
    ):  
        
        self.id = self._peppering(id) if id != ROOT_ID else ROOT_ID
        self.parent = parent
        self.children = []

        self.solution: models.Solution | None = solution
        self.reflection: models.Reflection = reflection

        self.value: float = 0
        self.visits: int = 0

    def __str__(self):
        return (
            f"Node ID: {self.id}"
        )
                    
    @property
    def is_not_root(self) -> bool:
        return self.id != ROOT_ID
    
    @property
    def haschildren(self) -> bool:
        return bool(len(self.children))
    
    @property
    def depth(self) -> int:
        return len(self.get_trajectory())


    def backpropagate(self, reward: float):
        """ 
        Follow the path to the root node and update the value of each node 
        
        Args:
            reward (float): The reward value to update the value of the node
        
        Returns:
            None

        """
        node: Node = self

        while node.is_not_root:
            node.visits += 1 
            node.value = (node.value * (node.visits - 1) + reward) / node.visits
            if node.parent is not None:
                node = node.parent
            else:
                break


    def get_trajectory(self) -> List["Node"]:
        """ 
        Get the path from the root node to the current node 

        Returns:
            List[Node]: The path from the root node to the current node

        """
        trajectory: List[Node] = [self]
        node: Node = self
        while node.is_not_root:

            if node.parent is not None:
                node = node.parent
                trajectory.append(node)

        return trajectory
    

    def _peppering(self, u_id: uuid.UUID) -> uuid.UUID:
        """
        Hash the UUID with the current object's memory address and random bits

        Args:
            u_id (uuid.UUID): The UUID to hash
        
        Returns:
            uuid.UUID: The hashed UUID
        
        """
        base_uuid = u_id.int
        where = id(self)
        random_bits = random.getrandbits(64)

        peppered = base_uuid ^ where ^ random_bits
        return uuid.UUID(int=peppered &((1 << 128) -1))



class MonteCarloTree:
    """
    ## MonteCarloTree

    MonteCarloTree is a tree structure that uses the Monte Carlo method to find the optimal solution.

    The key idea is to expand the tree by selecting the **best node** and then backpropagate the reward value to the root node.

    Selecting the best node is based on the **value** of the node, which is calculated by the UCB formula.

    This algorithm is useful because it doesn't select all nodes but only the best nodes, which can lead to the optimal solution.
    
    
    """

    def __init__(
        self,
        depth_limit: int = DEPTH_LIMIT,
        leafs_limit: int = LEAFS_LIMIT,        
        *,
        snapshot: bool = False,
        **kwargs
    ):
        """
        Args:
            depth_limit (int): The maximum depth of the tree
            leafs_limit (int): The maximum number of leaf nodes to expand
    
            snapshot (bool): Whether to save the snapshot of the tree or not
            **kwargs: Additional arguments to save the configuration of the tree

        ## Additional arguments:
            tree_id (str): The ID of the tree
            author (str): The author of the tree
            date (str): The date of the tree
            description (str): The description of the tree
            snapshot_name (str): The name of the snapshot file        
        
        """
        self.config = {}
        self.depth_limit = depth_limit
        self.leafs_limit = leafs_limit
        
        self.root = Node(
            id = ROOT_ID,
            reflection=ROOT_REFLECTION,
        )
        self.nodes: List[Node] = [self.root]      
        self.best_searchable_node = self.root
        self.snapshot = snapshot

        if snapshot:
            self.config['snapshot_name'] = kwargs.get("snapshot_name", f"MCT_{int(datetime.now().timestamp())}")

        self.config['tree_id'] = kwargs.get("tree_id", str(uuid.uuid4()))
        self.config['author'] = kwargs.get("author", "Sung Dong Kim")
        self.config['date'] = kwargs.get("date", datetime.now().isoformat())
        self.config['description'] = kwargs.get("description", "A wonderful MonteCarloTree!")
        

    def run(
        self, 
        query: str,
        loop: int = 3,
        pre_terminate: bool = False,
    ) -> models.Solution | None:
        """
        Run the MCT Search algorithm to find the optimal solution.

        Args:
            query (str): The question to find the solution
            loop (int): The number of iterations to run the algorithm
            pre_terminate (bool): Whether to terminate the algorithm early or not

        Returns:
            Optinal[solution]: The optimal solution or None if the solution is not found
        
        """

        for _ in range(loop):

            children = (
                self
                .select_leaf_node()
                .expand_child_nodes(query)                
            )
            terminatable, reason, solution = (
                self
                .backpropagate(children)
                .establish_hierarchy()
                .inspect_terminatable()   
            )

            if pre_terminate:
                if terminatable:
                    print(reason)
                    break

        if self.snapshot:
            self.save_snapshot(self.config['snapshot_name'])

        return solution
        

    def select_leaf_node(self) -> "MonteCarloTree":
        """ 
        Select the best node based on the UCB formula.
        """
        
        print("👀 Finding the best node...")
        best = self.root
        for n in self.nodes:
            
            if best.value <= n.value:

                if n.haschildren: # if the node has children, skip
                    continue

                best = n

        self.best_searchable_node = best
        print(f"🎉 Find the best Node! \nNode ID: {self.best_searchable_node.id}")
        print("-"*50)
        
        return self


    def expand_child_nodes(self, query: str) -> List[Node]:
        """ 
        Expand and excute acts on the child nodes based on the selected node.
        """
        
        father: Node = self.best_searchable_node
        print(f"🌱 Expand from Node: {father.id}, Range: {self.leafs_limit}")

        trajectory = father.get_trajectory()

        context = "\n"
        for node in trajectory:
            if node.id == ROOT_ID:
                continue
            else:
                solution = node.solution.model_dump(mode='json') if node.solution else {}
                context.join(str(solution) + "\n")
                
        print(f"📜 Context head: {context[:3]} ...")
        for _ in range(self.leafs_limit):
            
            solution = chat.solve(query=query, context=context)
            print(f"🔍 Solution: {solution}")
            reflection = chat.reflect(solution)
            print(f"🔍 Reflection: {reflection}")

            self.nodes.append(
                Node(
                    reflection= reflection,
                    solution=solution,
                    parent = father,
                )
            )

        return self.nodes[-self.leafs_limit:]
            

    def backpropagate(self, nodes: List[Node]) -> "MonteCarloTree":
        """ 
        Update the value of the nodes based on the reward value throughout the path to the root node 
        """
        print("🔄 Backpropagating the reward...")
        for node in nodes:
            reward = node.reflection.normalized_score

            node.backpropagate(reward)

        return self

    def establish_hierarchy(self) -> "MonteCarloTree":
        """ 
        Establish the hierarchy of the tree based on the parent-child relationship
        """
        print("🌳 Establishing the hierarchy...")
        for node in self.nodes:
            if node.parent:
                node.parent.children.append(node.id)

        return self


    def inspect_terminatable(self) -> Tuple[bool, str, models.Solution|None]:
        """
        Inspect whether the searching can be terminated or not
        """
        print("🔍 Inspecting the terminatable condition...")
        terminatable = False

        for node in self.nodes[-self.leafs_limit:]:
            
            if node.reflection.found_solution is True:
                terminatable = True
                reason = "📝 Find the Solution!"
                solution = node.solution
                break

            if node.depth > self.depth_limit:
                terminatable = True
                reason = "💀 Can't find the solution in the depth limit"
                solution = None
                break

        return terminatable, reason, solution

    
    def _snapshot(self) -> models.TreeSnapshot:
        """ Snapshot the tree structure and save it as a JSON file """

        snapshot= models.TreeSnapshot(
            tree_id=self.config['tree_id'],
            author=self.config['author'],
            date=self.config['date'],
            description=self.config['description'],
            nodes_snapshot = [
                models.NodeSnapshot(**{
                    "id": node.id, 
                    "value": node.value, 
                    "parent": node.parent.id if node.parent else None,
                    "solution": node.solution.model_dump(mode="json") if node.solution else None,
                    "reflection": node.reflection.model_dump(mode="json")
                })
                for node in self.nodes
            ],
            edges_snapshot=[
                models.EdgeSnapshot(**{"origin": node.parent.id, "to": node.id})
                for node in self.nodes if node.parent
            ]        
        )

        return snapshot

    def save_snapshot(self, filename):

        full_name = filename + ".json"

        with open(full_name, "w", encoding="utf-8") as f:
            dump = self._snapshot().model_dump(mode="json")        
            json.dump(dump, f, indent=4, ensure_ascii=False)