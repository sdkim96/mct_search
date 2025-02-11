from pydantic import BaseModel
from openai import OpenAI

import app.models as models

GROUD_MODEL="gpt-4o-mini"
SYSTEM_PROMPT = "You are a helpful assistant."

class BaseResponse(BaseModel):
    response: str

def invoke(
    user_prompt: str, 
    response_model,
    system_prompt: str | None = None,
):
    messages = [
        {"role": "system", "content": system_prompt if system_prompt else SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    if not response_model:
        response_model = BaseResponse 


    client = OpenAI()
    completion = client.beta.chat.completions.parse(
        model=GROUD_MODEL,
        messages=messages, # type: ignore
        response_format=response_model
    )
    

    answer = completion.choices[0].message.parsed   
    
    if answer:
        return answer
    

def solve(query: str, context: str) -> models.Solution:
    """ Propose A Solution to the given query """

    user_prompt = f"""        
    ## How-To
    Provide a solution to the given query based on the <context>.
    <context> could be none.
    If you are uncertain, answer could be null.
    But Please give a description of your reasoning.

    ## <context>
    {context}
    
    ## <query> 
    {query}        
    """

    solution: models.Solution = invoke(user_prompt=user_prompt, response_model=models.Solution) # type: ignore

    if solution:
        return solution

    else:
        raise
    

def reflect(solution: models.Solution) -> models.Reflection:
    """ Reflect on the given solution """

    user_prompt = f"""        
    
    ## How-To
    Reflect on the given solution.
    
    {solution.model_dump(mode='json')}   
    """
    
    reflection: models.Reflection = invoke(user_prompt=user_prompt, response_model=models.Reflection) # type: ignore

    if reflection:
        return reflection

    else:
        raise