from typing import Any, Dict, List
from pydantic import BaseModel
from enum import Enum

class type(Enum):
    Easy="Easy"
    Medium="Medium"
    Difficult="Difficult"


class Mete_data(BaseModel):
    function_name:str
    return_type:str
    variables: Dict[str, str]
    
class QuesSchema(BaseModel):
    title:str
    description:str
    type:str
    meta_data:Mete_data
    
    
  
    
class TestSchema(BaseModel):
    input_variables:Dict[str,Any] 
    output:str
    
    
class usercode(BaseModel):
    code:str