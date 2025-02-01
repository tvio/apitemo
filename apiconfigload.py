from config import logger
import os

from pydantic import BaseModel, field_validator
from pydantic_yaml import parse_yaml_raw_as
from typing import List,Optional

class ParamTypEnum(str):
    header = 'header'
    query = 'query'
    path = 'path'
class Request(BaseModel):
    class Config:
        extra = 'allow'
class Response(BaseModel):
    class Config:
        extra = 'allow' 
class Parameters(BaseModel):
    typ: ParamTypEnum
    hodnota: str
    typ:str
    popis: Optional[str] = None
class Jednotlive(BaseModel):
    id: int
    poradi: int
    metoda: str
    nazev: str
    uri: str
    parametry: Optional[Parameters] = None
    req: Optional[Request] = None
    res: Optional[Response] = None

class Opakovani(BaseModel):
    pocet: Optional[int] = None
    statusOk: Optional[bool] = None
    @field_validator('statusOK')
    def check_true(cls, value):
        if value is not True:
            raise ValueError('statusOk objektu Opakovani must be True')
        return value
class Sekvence(BaseModel):
    id: int
    poradi: int
    metoda: str
    nazev: str
    uri: str
    req: Optional[Request] = None
    res: Optional[Response] = None
    parametry: Optional[Parameters] = None
    opakovani: Optional[Opakovani] = None

class Monitor(BaseModel):
    server: str
    odesilatel: str
    emaily: List[str] 

class APIConfig(BaseModel):
    id: int
    nazev: str
    cert: bool
    prostredi : str
    url:str
    jednotlive: List[Jednotlive]
    sekvence: List[Sekvence]
    komponenty: List[Komponenty]
    monitor: List[Monitor]
    ciselniky: List[Ciselniky]

class APIConfigLoader:
    def __init__(self, directory='apiconfigs'):
        self.directory = directory

    def load_config(self, filename):
        filepath = os.path.join(self.directory, filename)
        logger.debug(f"Loading configuration file: {filepath}")
        try:
            with open(filepath, 'r') as file:
                yaml_data = file.read()
            config = parse_yaml_raw_as(APIConfig, yaml_data)
            logger.debug(f"Configuration loaded successfully: {config}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
            return None

# Example usage:
# loader = APIConfigLoader()
# config = loader.load_config('config.yaml')