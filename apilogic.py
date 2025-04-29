from apiclient import ApiClient
from typing import Any, Dict, Optional, Union, List
from apimodels import Promenna
from config import logger
from requests import Response
from datetime import datetime
import json
from utils import ft

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
       
    
    def callJednotlive(self, jednotlive_id):
        # Find the Jednotlive object with the matching id
        self.jednotlive = next(
            (j for j in self.config.jednotlive if j.id == jednotlive_id), None
        )
        if self.jednotlive is None:
            logger.error(f"Jednotlive with id {jednotlive_id} not found.")
            return None

        logger.debug(f"Processing jednotlive {jednotlive_id}: {self.jednotlive.nazev}")
        
        if self.jednotlive.parametry:
            result = self.zapracujParametry(self.jednotlive.parametry, self.jednotlive.url)
            if result is None:
                return None
            self.url = result['final_url']
            self.headers = result['headers']
        else:
            self.url = self.jednotlive.url
            self.headers = {}

        # Initialize empty request
        req = {}
        if self.jednotlive.req:
            # Process variables in request
            req = self.zapracujPromenneDoReq(self.jednotlive.req)
            if req is None:
                return None
            logger.debug(f"Request after processing variables: {req}")
            
        # Get limit from res configuration if it exists, otherwise use default of 10
        limit = 10  # Default limit
        if hasattr(self.jednotlive, 'res') and hasattr(self.jednotlive.res, 'limit'):
            limit = self.jednotlive.res.limit
            
        logger.debug(f"Making {self.jednotlive.metoda} request to {self.url}")
        
        # Ensure proper JSON serialization
        req_json = json.dumps(req, ensure_ascii=False)
        logger.info(f"{ft('Obsah requestu>>')} {req_json}")
        
        self.res = self.api_client.doReq(
            self.jednotlive.metoda, 
            self.url, 
            data=req_json,
            headers=self.headers,
            limit=limit
        )
        
        logger.debug(f"Response received: {self.res}")
        
        # Store variables from response
        stored_vars = self.ulozPromeneZRes(self.res)
        logger.debug(f"Stored variables after processing: {stored_vars}")
        
        return self.res

    def callSekvence(self,sekvence):
        self.sekvence = sekvence
        for krok in self.sekvence.kroky:
            self.callJednotlive(krok)   
    def zapracujParametry(self, parametry, url):
        self.base_url = url
        self.path_url = self.base_url.rstrip('/')  # Remove trailing slash from base URL
        self.query_url = ""
        self.headers = {}
        
        # Track variables used in parameters
        param_vars = []
        
        # Nejdřív zpracujeme path parametry
        for parametr in parametry:
            if parametr.typ == 'path':
                # Check if hodnota contains a variable anywhere in the string
                if isinstance(parametr.hodnota, str):
                    # Split the path and handle each part
                    path_parts = parametr.hodnota.split('/')
                    for part in path_parts:
                        if part.startswith('$'):
                            # Find the variable in promenne_list
                            promenna = next((p for p in self.promenne_list if p['name'] == part[1:]), None)
                            if promenna and promenna['value'] is not None:
                                self.path_url += f"/{promenna['value']}"
                                param_vars.append(f"path: {part[1:]} = {promenna['value']}")
                                logger.debug(f"Found variable in path: {part[1:]}, value: {promenna['value']}")
                            else:
                                logger.error(f"Required variable {part} is not set. Exiting to menu.")
                                input("\nPress Enter to return to menu...")
                                return None
                        elif part:  # Only add non-empty parts
                            self.path_url += f"/{part}"
                
        # Zpracujeme query parametry
        for i, parametr in enumerate(parametry):
            if parametr.typ == 'query':
                # Check if hodnota contains a variable
                if isinstance(parametr.hodnota, str) and parametr.hodnota.startswith('$'):
                    # Find the variable in promenne_list
                    promenna = next((p for p in self.promenne_list if p['name'] == parametr.hodnota[1:]), None)
                    if promenna and promenna['value'] is not None:
                        hodnota = promenna['value']
                        param_vars.append(f"query: {parametr.nazev} = {hodnota} (from {parametr.hodnota[1:]})")
                        logger.debug(f"Found variable in query: {parametr.nazev}, value: {hodnota}")
                    else:
                        logger.error(f"Required variable {parametr.hodnota} is not set. Exiting to menu.")
                        input("\nPress Enter to return to menu...")
                        return None
                else:
                    hodnota = parametr.hodnota
                    
                # První query parametr začíná ?, další používají &
                delimiter = '?' if i == 0 else '&'
                self.query_url += f"{delimiter}{parametr.nazev}={hodnota}"
                
        # Nakonec zpracujeme hlavičky
        for parametr in parametry:
            if parametr.typ == 'header':
                # Check if hodnota contains a variable
                if isinstance(parametr.hodnota, str) and parametr.hodnota.startswith('$'):
                    # Find the variable in promenne_list
                    promenna = next((p for p in self.promenne_list if p['name'] == parametr.hodnota[1:]), None)
                    if promenna and promenna['value'] is not None:
                        self.headers[parametr.nazev] = promenna['value']
                        param_vars.append(f"header: {parametr.nazev} = {promenna['value']} (from {parametr.hodnota[1:]})")
                        logger.debug(f"Found variable in header: {parametr.nazev}, value: {promenna['value']}")
                    else:
                        logger.error(f"Required variable {parametr.hodnota} is not set. Exiting to menu.")
                        input("\nPress Enter to return to menu...")
                        return None
                else:
                    self.headers[parametr.nazev] = parametr.hodnota
                
        # Sestavíme finální URL
        self.final_url = self.path_url + self.query_url
        
        # Log all variables used in parameters at INFO level
        if param_vars:
            logger.info("Variables used in parameters:")
            for var in param_vars:
                logger.info(f"  {var}")
                
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
        self.promenne_list = []
        try:
            jednotlive_list = self.config.jednotlive or []
            for jednotlive in jednotlive_list:
                jednotlive_id = jednotlive.id
                logger.debug(f"Processing jednotlive {jednotlive_id}: {jednotlive.nazev}")
                
                # Check req
                if jednotlive.req:
                    logger.debug(f"Checking req for variables in jednotlive {jednotlive_id}")
                    self._find_vars_in_pydantic(jednotlive.req, jednotlive_id, 'req')
                
                # Check res
                if jednotlive.res:
                    logger.debug(f"Checking res for variables in jednotlive {jednotlive_id}")
                    self._find_vars_in_pydantic(jednotlive.res, jednotlive_id, 'res')
                
                # Check parametry
                if jednotlive.parametry:
                    logger.debug(f"Checking parametry for variables in jednotlive {jednotlive_id}")
                    for param in jednotlive.parametry:
                        typ = param.typ
                        nazev = param.nazev or ''
                        hodnota = param.hodnota
                        # Check for variables in hodnota
                        if isinstance(hodnota, str) and hodnota.startswith('$'):
                            self.promenne_list.append({
                                'id': jednotlive_id,
                                'typ': f'{typ}',
                                'name': hodnota[1:],
                                'value': None
                            })
                            logger.debug(f"Found variable in hodnota: {hodnota[1:]}")
                        # Check for variables in nazev
                        if isinstance(nazev, str) and nazev.startswith('$'):
                            self.promenne_list.append({
                                'id': jednotlive_id,
                                'typ': f'{typ}',
                                'name': nazev[1:],
                                'value': None
                            })
                            logger.debug(f"Found variable in nazev: {nazev[1:]}")
                        # Check for variables in path values
                        if typ == 'path' and isinstance(hodnota, str) and '/' in hodnota:
                            path_parts = hodnota.split('/')
                            for part in path_parts:
                                if part.startswith('$'):
                                    self.promenne_list.append({
                                        'id': jednotlive_id,
                                        'typ': f'{typ}',
                                        'name': part[1:],
                                        'value': None
                                    })
                                    logger.debug(f"Found variable in path: {part[1:]}")
            
            logger.debug(f"Final promenne_list: {self.promenne_list}")
        except Exception as e:
            logger.error(f"Error in najdiPromenne: {e}")
            logger.debug(f"Promenne list: {self.promenne_list}")

    def _find_vars_in_pydantic(self, obj, jednotlive_id, typ):
        """
        Helper to recursively find $variables in a Pydantic model (req or res).
        """
        logger.debug(f"Finding variables in {typ} for jednotlive {jednotlive_id}")
        if hasattr(obj, 'model_dump'):
            data = obj.model_dump()
        elif isinstance(obj, dict):
            data = obj
        else:
            return

        logger.debug(f"Processing data: {data}")
        for key, value in data.items():
            if isinstance(value, str) and value.startswith('$'):
                self.promenne_list.append({
                    'id': jednotlive_id,
                    'typ': typ,
                    'name': value[1:],
                    'value': None
                })
                logger.debug(f"Found variable {value[1:]} in {typ}")
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
    def zapracujPromenneDoReq(self, req):
        if not req:
            return req
            
        # Convert to dict if it's a Pydantic model
        if hasattr(req, '__class__') and hasattr(req.__class__, 'model_dump'):
            req = req.model_dump()
            
        # Create a copy of the request to modify
        req_copy = req.copy()
        
        # Track variables that were replaced
        replaced_vars = []
        
        # Find all variables that need to be replaced
        for key, value in req_copy.items():
            # Check if the value is a variable reference (starts with $)
            if isinstance(value, str) and value.startswith('$'):
                var_name = value[1:]  # Remove the $ prefix
                
                # Special handling for timestamp
                if var_name == 'timestamp':
                    current_time = datetime.now()
                    req_copy[key] = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    replaced_vars.append(f"{key}: {req_copy[key]} (timestamp)")
                    logger.debug(f"Inserted current timestamp {req_copy[key]} for {key}")
                    continue
                
                # Find the variable in promenne_list by name
                promenna = next((p for p in self.promenne_list if p.get('name') == var_name), None)
                
                if promenna:
                    if promenna.get('value') is None:
                        logger.error(f"Required variable {var_name} is not set. Exiting to menu.")
                        input("\nPress Enter to return to menu...")
                        return None
                    req_copy[key] = promenna.get('value')
                    replaced_vars.append(f"{key}: {promenna.get('value')} (from {var_name})")
                    logger.debug(f"Replaced {key} with value {promenna.get('value')} from variable {var_name}")
                else:
                    logger.error(f"Variable {var_name} not found in stored variables. Exiting to menu.")
                    input("\nPress Enter to return to menu...")
                    return None
        
        # Log all replaced variables at INFO level
        if replaced_vars:
            logger.info(f"{ft('Variables loaded into request:')}")
            for var in replaced_vars:
                logger.info(f"  {var}")
        
        logger.debug(f"Request after variable replacement: {req_copy}")
        return req_copy

    def _find_nested_value(self, data, target_key):
        """
        Recursively search for a key in nested dictionaries and lists.
        Returns the first value found for the target key.
        """
        if isinstance(data, dict):
            if target_key in data:
                return data[target_key]
            for value in data.values():
                result = self._find_nested_value(value, target_key)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_nested_value(item, target_key)
                if result is not None:
                    return result
        return None

    def ulozPromeneZRes(self, res: Union[Response, dict, list, None]) -> List[dict]:
        """
        Store variables from API response.
        
        Args:
            res: API response, can be a Response object, dictionary, list, or None
            
        Returns:
            List of stored variables with type 'res'
        """
        if not res:
            logger.debug("Empty response received")
            return []
            
        # Handle Response object by getting its JSON data
        if isinstance(res, Response):
            try:
                res_data = res.json()
                logger.debug(f"Response data: {res_data}")
            except Exception as e:
                logger.error(f"Failed to parse response JSON: {e}")
                return []
        else:
            res_data = res
            
        # Convert Pydantic model to dict if needed
        if hasattr(res_data, '__class__') and hasattr(res_data.__class__, 'model_dump'):
            res_data = res_data.model_dump()
            
        # Apply limit if specified in res configuration
        if self.jednotlive is not None and hasattr(self.jednotlive, 'res'):
            res_config = self.jednotlive.res
            if hasattr(res_config, 'limit') and res_config.limit is not None:
                limit = res_config.limit
                if isinstance(res_data, dict):
                    # For dictionary responses, limit the number of items in each key's value if it's a list
                    limited_data = {}
                    for key, value in res_data.items():
                        if isinstance(value, list) and limit > 0:
                            limited_data[key] = value[:limit]
                            logger.debug(f"Limited {key} to {limit} items")
                        else:
                            limited_data[key] = value
                    res_data = limited_data
                elif isinstance(res_data, list) and limit > 0:
                    res_data = res_data[:limit]
                    logger.debug(f"Limited response list to {limit} items")
            
        # Store variables from the response object
        stored_vars = []
        loaded_vars = []
        for promenna in self.promenne_list:
            if not promenna or promenna['typ'] != 'res':
                continue
                
            name = promenna['name']
            if not name:
                continue
                
            # Use recursive search to find the attribute
            value = self._find_nested_value(res_data, name)
            if value is not None:
                promenna['value'] = value
                stored_vars.append(f"{name}={value}")
                loaded_vars.append(f"{name}: {value}")
                logger.debug(f"Stored variable {name} with value {value}")
            else:
                logger.debug(f"Variable {name} not found in response")
        
        # Log all loaded variables at INFO level
        if loaded_vars:
            logger.info(f"{ft('Variables loaded from response:')}")
            for var in loaded_vars:
                logger.info(f"  {var}")
        
        logger.debug(f"Stored variables: {stored_vars}")
        return [x for x in self.promenne_list if x and x['typ'] == 'res']

