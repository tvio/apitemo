from apiclient import ApiClient
from typing import Any, Dict, Optional
from apimodels import Promenna

class APILogicController:
    def __init__(self, config):
        self.config = config
        self.api_client = ApiClient(
            id=self.config.id,
            url=self.config.url,
            nazev=self.config.nazev,
            prostredi=self.config.prostredi,
            certFile=self.config.cert.nazevSouboru if self.config.cert else None,
            password=self.config.cert.heslo if self.config.cert else None,
        )
        # Only call auth() if certificate configuration exists
        if self.config.cert:
            self.api_client.auth()
        
    def vyrobaRequestu(self, req):
        if req:
            # Převede Pydantic model na dict, který requests.post/put
            # automaticky převede na JSON
            return req.model_dump()
        return {}
    
    
    def callJednotlive(self, jednotliveId):
        self.jednotlive = self.config.jednotlive[jednotliveId]
        if self.jednotlive.parametry:
            result = self.parametry(self.jednotlive.parametry, self.jednotlive.url)
            self.url = result['final_url']
            self.headers = result['headers']
        else:
            self.url = self.jednotlive.url
            self.headers = {}
        
        # Použijeme novou metodu pro přípravu dat
        req_con = self.vyrobaRequestu(self.jednotlive.req)
            
        self.res = self.api_client.doReq(
            self.jednotlive.metoda, 
            self.url, 
            data=req_con,
            headers=self.headers
        )
        return self.res

    def callSekvence(self,sekvence):
        self.sekvence = sekvence
        for krok in self.sekvence.kroky:
            self.callJednotlive(krok)   
    def parametry(self, parametry, url):
        self.base_url = url
        self.path_url = self.base_url
        self.query_url = ""
        self.headers = {}
        
        # Nejdřív zpracujeme path parametry
        for parametr in parametry:
            if parametr.typ == 'path':
                self.path_url += f"/{parametr.nazev}/{parametr.hodnota}"
                
        # Zpracujeme query parametry
        for i, parametr in enumerate(parametry):
            if parametr.typ == 'query':
                # První query parametr začíná ?, další používají &
                delimiter = '?' if i == 0 else '&'
                self.query_url += f"{delimiter}{parametr.nazev}={parametr.hodnota}"
                
        # Nakonec zpracujeme hlavičky
        for parametr in parametry:
            if parametr.typ == 'header':
                self.headers[parametr.nazev] = parametr.hodnota
                
        # Sestavíme finální URL
        self.final_url = self.base_url + self.path_url + self.query_url
                
        return {
          
            'final_url': self.final_url,
            'headers': self.headers
        }
    def ulozPromenne(self, name: str, value: Any):
        """Uloží proměnnou do objektu"""
        setattr(self.config.promenne, name, value)
    #potrebuji rozlisist parametr v req a v res a v parametru
    def najdiPromenne(self, data: dict) -> None:
        """Prochází data a hledá parametry označené $ """
        # Check if input is a dictionary, if not return immediately
        if not isinstance(data, dict):
            return
        # Iterate through each key-value pair in the dictionary. To znamena pridat typ (req/res/path/query/header), ulozit value a nazev atributu nebo bez nazvu
        for key, value in data.items():
            # Check if value is a string and starts with $ (parameter marker)
            if isinstance(value, str) and value.startswith('$'):
                # Extract parameter name by removing $ prefix
                param_name = value[1:]
                # Check if parameter doesn't exist in config.promenne
                if not hasattr(self.config.promenne, param_name):
                    # Store parameter with None as initial value
                    self.ulozPromenne(param_name, None)
            # If value is a nested dictionary, recursively search it
            elif isinstance(value, dict):
                self.najdiPromenne(value)
            # If value is a list, check each item
            elif isinstance(value, list):
                # Iterate through each item in the list
                for item in value:
                    # If item is a dictionary, recursively search it
                    if isinstance(item, dict):
                        self.najdiPromenne(item)

  