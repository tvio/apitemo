from pydantic import BaseModel, model_validator
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
    res: Optional[Response] = None  # Fixed: Removed extra bracket.
    limit: Optional[int] = None

class Opakovani(BaseModel):
    pocet: Optional[int] = None
    statusOk: Optional[bool] = None
    class Config:
        arbitrary_types_allowed = True

class Kroky(BaseModel):
    id: int
    metoda: str
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
    nazev: str

class Interval(BaseModel):
    hodnota: int
    jendotka: str

class Monitor(BaseModel):
    server: str
    odesilatel: str
    emaily: List[str]
    pocetVad: int
    casOdpoved: Optional[int] = None
    interval: Interval
    jednotlive: Optional[List[int]] = None
    sekvence: Optional[List[int]] = None

    @model_validator(mode='after')
    def check_at_least_one(cls, instance):
        if not any([instance.jednotlive, instance.sekvence]):
            raise ValueError('At least one of jednotlive or sekvence must be provided in Monitor')
        return instance

class Ciselniky(BaseModel):
    id: int
    nazev: str
    hodnota: str

class Cert(BaseModel):
    nazevSouboru: str
    heslo: str

class APIConfig(BaseModel):
    id: int
    nazev: str
    cert: Optional[Cert] = None
    prostredi: str
    url: str
    jednotlive: Optional[List[Jednotlive]] = None
    sekvence: Optional[List[Sekvence]] = None
    monitor: Optional[Monitor] = None
    ciselniky: Optional[List[Ciselniky]] = None
    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def check_at_least_one(cls, instance):
        if not any([instance.jednotlive, instance.sekvence, instance.monitor]):
            raise ValueError('At least one of jednotlive, sekvence, or monitor must be provided')
        return instance
