from apiclient import ApiClient
from typing import Any, Dict, Optional
from apimodels import Promenna
from config import logger
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
        self.najdiPromenne()
        logger.debug(f"Promenne: {self.promenne_list}")
    def vyrobaRequestu(self, req):
        if req:
            # Převede Pydantic model na dict, který requests.post/put
            # automaticky převede na JSON
            return req.model_dump()
        return {}
    
    
    def callJednotlive(self, jednotlive_id):
        # Find the Jednotlive object with the matching id
        self.jednotlive = next(
            (j for j in self.config.jednotlive if j.id == jednotlive_id), None
        )
        if self.jednotlive is None:
            logger.error(f"Jednotlive with id {jednotlive_id} not found.")
            return None
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
#     def ulozPromenne(self, name: str, value: Any):
#         """Uloží proměnnou do objektu"""
#         setattr(self.config.promenne, name, value)
#     #potrebuji rozlisist parametr v req a v res a v parametru
#   #potrebuji rozlisist parametr v req a v res a v parametru
    def najdiPromenne(self) -> None:
        """
        Prochází jednotlive v configu a hledá proměnné označené $ v req, res, parametry.
        Ukládá je do self.promenne_list jako dict s id, type, name, value.
        """
        logger.debug("Calling najdiPromenne()")
        print("najdiPromenne called")
        self.promenne_list = []
        try:
            jednotlive_list = self.config.jednotlive or []
            for jednotlive in jednotlive_list:
                jednotlive_id = jednotlive.id
                # Check req
                if jednotlive.req:
                    self._find_vars_in_pydantic(jednotlive.req, jednotlive_id, 'req')
                # Check res
                if jednotlive.res:
                    self._find_vars_in_pydantic(jednotlive.res, jednotlive_id, 'res')
                # Check parametry
                if jednotlive.parametry:
                    for param in jednotlive.parametry:
                        typ = param.typ
                        nazev = param.nazev or ''
                        hodnota = param.hodnota
                        if isinstance(hodnota, str) and hodnota.startswith('$'):
                            self.promenne_list.append({
                                'id': jednotlive_id,
                                'type': f'{typ} parameter',
                                'name': hodnota[1:],
                                'value': None
                            })
                        if isinstance(nazev, str) and nazev.startswith('$'):
                            self.promenne_list.append({
                                'id': jednotlive_id,
                                'type': f'{typ} parameter',
                                'name': nazev[1:],
                                'value': None
                            })
        except Exception as e:
            logger.error(f"Error in najdiPromenne: {e}")

    def _find_vars_in_pydantic(self, obj, jednotlive_id, typ):
        """
        Helper to recursively find $variables in a Pydantic model (req or res).
        """
        if hasattr(obj, 'model_dump'):
            data = obj.model_dump()
        elif isinstance(obj, dict):
            data = obj
        else:
            return

        for key, value in data.items():
            if isinstance(value, str) and value.startswith('$'):
                self.promenne_list.append({
                    'id': jednotlive_id,
                    'type': typ,
                    'name': value[1:],
                    'value': None
                })
            elif isinstance(value, dict):
                # Try to get the original attribute if possible (for nested Pydantic models)
                attr = getattr(obj, key, value)
                self._find_vars_in_pydantic(attr, jednotlive_id, typ)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    attr = getattr(obj, key, value)
                    if isinstance(attr, list) and len(attr) > idx:
                        self._find_vars_in_pydantic(attr[idx], jednotlive_id, typ)
                    elif isinstance(item, dict):
                        self._find_vars_in_pydantic(item, jednotlive_id, typ)