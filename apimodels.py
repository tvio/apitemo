from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict, Any

class Request(BaseModel):
    """Model pro obecný request"""
    model_config = {
        'extra': 'allow'  # Povolí dodatečné atributy
    }

class Response(BaseModel):
    """Model pro obecnou response"""
    model_config = {
        'extra': 'allow'
    }

class Parameters(BaseModel):
    """Model pro parametry API volání"""
    typ: str
    nazev: Optional[str] = None
    hodnota: str
    popis: Optional[str] = None

    model_config = {
        'arbitrary_types_allowed': True
    }

class Jednotlive(BaseModel):
    """Model pro jednotlivé API volání"""
    id: int
    metoda: str
    nazev: str
    uri: str
    parametry: Optional[List[Parameters]] = None
    req: Optional[Request] = None
    res: Optional[Response] = None
    limit: Optional[int] = None
    api_config_url: Optional[str] = None

    @property
    def url(self) -> str:
        return f"{self.api_config_url}{self.uri}"

class Opakovani(BaseModel):
    pocet: Optional[int] = None
    statusOk: Optional[bool] = None
    class Config:
        arbitrary_types_allowed = True

# class Kroky(BaseModel):
#     id: int
#     metoda: str
#     uri: str
#     req: Optional[Request] = None
#     res: Optional[Response] = None
#     parametry: Optional[List[Parameters]] = None
#     opakovani: Optional[Opakovani] = None
#     limit: Optional[int] = None
#     api_config_url: Optional[str] = None
#     class Config:
#         arbitrary_types_allowed = True

#     @property
#     def url(self):
#         return f"{self.api_config_url}{self.uri}"

# sekvence nove jen jako pole kroku
class Sekvence(BaseModel):
    id: int
    kroky: List[int]   
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

class Promenna(BaseModel):
    """Model pro proměnné"""
    nazev: Optional[str] = None
    hodnota: Optional[Any] = None
   
    model_config = {
        'extra': 'allow'  # Allow dynamic field creation
    }

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
    # neni soucasti yaml configu ale je to objekt pro ulozeni promennych
    promenne: Optional[Promenna] = None
    
    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode='after')
    def check_at_least_one(cls, instance):
        if not any([instance.jednotlive, instance.sekvence, instance.monitor]):
            raise ValueError('At least one of jednotlive, sekvence, or monitor must be provided')
        return instance

    def __init__(self, **data):
        super().__init__(**data)
        if self.promenne is None:
            self.promenne = Promenna()
        # Set the api_config_url for each Jednotlive and Kroky
        if self.jednotlive:
            for item in self.jednotlive:
                item.api_config_url = self.url
      
