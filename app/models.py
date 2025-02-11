import uuid
from typing import List
from pydantic import BaseModel, Field 

class Answer(BaseModel):
    answer: str | None = Field(
        description="Answer to the question. If it's hard to judge, None",
        default=None
    )
    description: str = Field(
        description="Description of the answer",
    )

    def __repr__(self):
        return (
            f"answer: {self.answer[:3] if self.answer else 'None'}, description: {self.description}\n"
        )

    def __str__(self):
        return (
            f"answer: {self.answer[:3] if self.answer else 'None'}..., description: {self.description}\n"
        )


class Solution(BaseModel):
    
    query: str
    answer: Answer

    def __str__(self):
        return (
            f"question: {self.query}, answer: {self.answer}\n"            
            "---------------------------------------------------------\n"
        )


class Reflection(BaseModel):

    reflections: str = Field(
        description="Propose rationality, appropriativity and correctness of the answer",
    )
    score: int = Field(
        description="Score based on the reflection. from 0 to 9",
    )
    found_solution: bool = Field(
        description="Whether the solution is found or not",
    )

    def __str__(self):
        return (
            f"reflection: {self.reflections}, score: {self.score}, found_solution: {self.found_solution}\n"
            "---------------------------------------------------------\n"
        )
        
    @property
    def normalized_score(self):
        return self.score / 10.0


class NodeSnapshot(BaseModel):
    id: uuid.UUID
    value: float
    parent: uuid.UUID | None

    solution: Solution | None
    reflection: Reflection

class EdgeSnapshot(BaseModel):
    origin: uuid.UUID
    to: uuid.UUID

class TreeSnapshot(BaseModel):
    tree_id: uuid.UUID
    author: str
    date: str
    description: str

    nodes_snapshot: List[NodeSnapshot]
    edges_snapshot: List[EdgeSnapshot]
    
    

