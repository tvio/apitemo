import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
import base64
import tempfile
from contextlib import contextmanager
from config import logger
from dataclasses import dataclass
from typing import Optional
import os
from requests import Session
from utils import ft
import json



@contextmanager
def pfx_to_pem(pfx_path, pfx_password):
    # Get the absolute path to the cert directory relative to the script location
    cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cert')
    
    # Ensure cert directory exists
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    # Create full path to the pfx file
    full_pfx_path = os.path.join(cert_dir, pfx_path)
    
    with open(full_pfx_path, 'rb') as pfx_file:
        pfx_data = pfx_file.read()
    private_key, main_cert, add_certs = load_key_and_certificates(pfx_data, pfx_password.encode('utf-8'))
    with tempfile.NamedTemporaryFile(delete=False) as t_pem:
        with open(t_pem.name, 'wb') as pem_file:
            pem_file.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
            pem_file.write(main_cert.public_bytes(Encoding.PEM))
            for ca in add_certs:
                pem_file.write(ca.public_bytes(Encoding.PEM))
        yield t_pem.name

@dataclass
class ApiClient:
    id: int
    url: str
    nazev: str
    prostredi: str
    certFile: Optional[str] 
    password: Optional[str]
    def __post_init__(self):
        self.timeout = (10, 10)
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
                

    def auth(self):
           with pfx_to_pem(self.certFile, self.password) as c:
            self.cert = c
            logger.debug("Certificate loaded successfully")


    def doReq(self, htmlOperace, url, data={}, headers={}, limit=10):
        logger.info(f"{ft('Provedu request')} {htmlOperace} {ft('na URL>>')} {url}")
        if data != {}:
            logger.info(f"{ft('Obsah requestu>>')} {data}")
        try:
            if htmlOperace == 'GET':
                res = self.session.get(url , 
                                     cert=self.cert, 
                                     timeout=self.timeout,
                                     headers=headers)
            elif htmlOperace == 'POST':
                # Ensure data is a dictionary, not a string
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass
                res = self.session.post(url, 
                                      cert=self.cert, 
                                      timeout=self.timeout, 
                                      json=data,
                                      headers=headers)
            elif htmlOperace == 'PUT':
                # Ensure data is a dictionary, not a string
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass
                res = self.session.put(url, 
                                     cert=self.cert, 
                                     timeout=self.timeout, 
                                     json=data,
                                     headers=headers)
            elif htmlOperace == 'DELETE':
                res = self.session.delete(url, 
                                        cert=self.cert, 
                                        timeout=self.timeout,
                                        headers=headers)
            
            # Handle response limiting
            if res.status_code == 200:
                try:
                    response_data = res.json()
                    if isinstance(response_data, dict):
                        # For dictionary responses, limit list values
                        limited_data = {}
                        for key, value in response_data.items():
                            if isinstance(value, list):
                                limited_data[key] = value[:limit]
                            else:
                                limited_data[key] = value
                        logger.info(f"{ft('Obsah response>>')} {res.status_code}, Response>>{limited_data}")
                    elif isinstance(response_data, list):
                        # For list responses, limit the list
                        limited_data = response_data[:limit]
                        logger.info(f"{ft('Obsah response>>')} {res.status_code}, Response>>{limited_data}")
                    else:
                        logger.info(f"{ft('Obsah response>>')} {res.status_code}, Response>>{response_data}")
                except ValueError:
                    # If JSON parsing fails, log the original response
                    logger.info(f"{ft('Obsah response>>')} {res.status_code}, Response>>{res.text}")
            else:
                logger.info(f"{ft('Obsah response>>')} {res.status_code}, Response>>{res.text}")
            return res
        except ConnectionError:
            logger.info(f"{ft('ConnectionError:')} Nelze navazat spojeni")
            return CustomResponse('{"error": "Nelze navazat spojeni"}', 503)
        except requests.exceptions.Timeout as err:
            if err.response and err.response.status_code != 500:
                logger.info(f"{ft('Timeout error with response:')} {err.response.text}")
                return err.response
            elif err.response and err.response.status_code == 500:
                logger.info(f"{ft('Timeout error:')} Internal Server Error")
                return CustomResponse('{"error": "Internal Server Error"}', 500)
        except requests.HTTPError as http_err:
            logger.debug(f"{ft('HTTPError occurred:')} {http_err}")
            return CustomResponse(f'{{"error": "HTTP error occurred: {http_err}"}}', 500)
        except Exception as err:
            logger.debug(f"{ft('An error occurred:')} {err}")
            return CustomResponse(f'{{"error": "An error occurred: {err}"}}', 500)



# Example usage:
# client = ApiClient()
# client.auth(1)
# response = client.doReq('get', '/some-operation')




class CustomResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code