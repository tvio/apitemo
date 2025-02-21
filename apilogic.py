from apiclient import ApiClient
from typing import Any, Dict, Optional
from apimodels import Promenna

class APILogicController:
    def __init__(self, config):
        self.config = config
        self.promenne = Promenna()
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
        
    def callJednotlive(self, jednotlive):
        self.jednotlive = jednotlive
        if jednotlive.parametry:
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
        setattr(self.promenne, name, value)

  