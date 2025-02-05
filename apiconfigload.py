from config import logger
import os
from pydantic import BaseModel, ValidationError, model_validator
from pydantic_yaml import parse_yaml_raw_as
from typing import List, Optional


class Request(BaseModel):
    class Config:
        extra = 'allow'
class Response(BaseModel):
    class Config:
        extra = 'allow' 
class Parameters(BaseModel):
    typ: str
    nazev: Optional[str] = None
    hodnota: str
    popis: Optional[str] = None
    class Config:
        arbitrary_types_allowed = True

class Jednotlive(BaseModel):
    id: int
    metoda: str
    nazev: str
    uri: str
    parametry: Optional[List[Parameters]] = None
    req: Optional[Request] = None
    res: Optional[Response] = None
    limit: Optional[int] = None

class Opakovani(BaseModel):
    pocet: Optional[int] = None
    statusOk: Optional[bool] = None
    class Config:
        arbitrary_types_allowed = True
class Kroky(BaseModel):
    id: int
    metoda: str
    nazev: str
    uri: str
    req: Optional[Request] = None
    res: Optional[Response] = None
    parametry: Optional[List[Parameters]] = None
    opakovani: Optional[Opakovani] = None
    limit: Optional[int] = None
    class Config:
        arbitrary_types_allowed = True

class Sekvence(BaseModel):
    id: int
    kroky: List[Kroky]
    class Config:
        arbitrary_types_allowed = True
class Interval(BaseModel):
    hodnota: int
    jendotka: str
class Monitor(BaseModel):
    server: str
    odesilatel: str
    emaily: List[str] 
    pocetVad: int
    # v sec
    casOdpovedi: Optional[int] = None
    interval: Interval
    jednotlive: Optional[List[int]]= None
    Sekvence: Optional[List[int]]= None

class Ciselniky(BaseModel):
    nazev: str
    metoda: str
    url : str
    atribut: str
    limit: Optional[int] = None
    class Config:
        arbitrary_types_allowed = True

class Cert(BaseModel):
    nazevSouboru: str
    heslo: str
    
class APIConfig(BaseModel):
    id: int
    nazev: str
    cert: Optional[Cert] = None
    prostredi : str
    url:str
    jednotlive: Optional[List[Jednotlive]] = None
    sekvence: Optional[ List[Sekvence]] = None
    monitor: Optional[Monitor] = None
    ciselniky: Optional[ List['Ciselniky']] = None
    class Config:
        arbitrary_types_allowed = True
    @model_validator(mode='after')
    def check_at_least_one(cls, values):
        if not any([values.get('jednotlive'), values.get('sekvence'), values.get('monitor')]):
            raise ValueError('At least one of jednotlive, sekvence, or monitor must be provided')
        return values

class APIConfigLoader:
    def __init__(self, directory='apiconfigs'):
        self.directory = directory

    def load_config(self, filepath):
        logger.debug(f"Loading configuration file: {filepath}")
        if not os.path.exists(filepath):
            logger.error(f"Configuration file not found: {filepath}")
            return None
        try:
            with open(filepath, 'r') as file:
                yaml_data = file.read()
            config = parse_yaml_raw_as(APIConfig, yaml_data)
            logger.debug(f"Configuration loaded successfully: {config}")
            return config
        except ValidationError as e:
            logger.error(f"Validation error: {e.errors()}")
            return None
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
            return None

