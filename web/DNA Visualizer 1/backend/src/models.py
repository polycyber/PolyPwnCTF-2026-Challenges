from pydantic import BaseModel

class DNAProfile(BaseModel):
    mode: str
    length: int

class DNAGeneration(BaseModel):
    sequence: str
