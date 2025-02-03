from config import logger
import os
from pydantic import BaseModel, ValidationError
from pydantic_yaml import parse_yaml_raw_as
from typing import List,Optional


class Request(BaseModel):
    class Config:
        extra = 'allow'
class Response(BaseModel):
    class Config:
        extra = 'allow' 
class Parameters(BaseModel):
    typ: str
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

class Opakovani(BaseModel):
    pocet: Optional[int] = None
    statusOk: Optional[bool] = None
    class Config:
        arbitrary_types_allowed = True
class Sekvence(BaseModel):
    id: int
    poradi: int
    metoda: str
    nazev: str
    uri: str
    req: Optional[Request] = None
    res: Optional[Response] = None
    parametry: Optional[List[Parameters]] = None
    opakovani: Optional[Opakovani] = None
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
    interval: Interval
    jednotlive: List[Jednotlive]

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
    cert: Optional[Cert]
    prostredi : str
    url:str
    jednotlive: Optional[List[Jednotlive]]
    #upravit sekvence na objekty zrusit id
    sekvence: Optional[ List[Sekvence]]
    monitor: Optional[Monitor]
    ciselniky: List['Ciselniky']
    class Config:
        arbitrary_types_allowed = True
class APIConfigLoader:
    def __init__(self, directory='apiconfigs'):
        self.directory = directory

    def load_config(self, filename):
        filepath = os.path.join(self.directory, filename)
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


