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



@contextmanager
def pfx_to_pem(pfx_path, pfx_password):
    with open(pfx_path, 'rb') as pfx_file:
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
           with pfx_to_pem(self.cert, self.url) as c:
            self.cert = c
            logger.debug("Certificate loaded successfully")


    def doReq(self, htmlOperace, operace, data={}):
        logger.info(f"Metoda doReq na URL>> {self.url + operace}")
        logger.info(f"Metoda doReq request>> {data}")
        try:
            if htmlOperace == 'get':
                res = self.session.get(self.url + operace, cert=self.cert, timeout=self.timeout)
            elif htmlOperace == 'post':
                res = self.session.post(self.url + operace, cert=self.cert, timeout=self.timeout, json=data)
            elif htmlOperace == 'put':
                res = self.session.put(self.url + operace, cert=self.cert, timeout=self.timeout, json=data)
            elif htmlOperace == 'delete':
                res = self.session.delete(self.url + operace, cert=self.cert, timeout=self.timeout)
            logger.info(f"Metoda doReq response>> {res.status_code}, Response>>{res.text}")
            return res
        except ConnectionError:
            logger.info('ConnectionError: Nelze navazat spojeni')
            return CustomResponse('{"error": "Nelze navazat spojeni"}', 503)
        except requests.exceptions.Timeout as err:
            if err.response and err.response.status_code != 500:
                logger.info(f'Timeout error with response: {err.response.text}')
                return err.response
            elif err.response and err.response.status_code == 500:
                logger.info('Timeout error: Internal Server Error')
                return CustomResponse('{"error": "Internal Server Error"}', 500)
        except requests.HTTPError as http_err:
            logger.debug(f'HTTPError occurred: {http_err}')
            return CustomResponse(f'{{"error": "HTTP error occurred: {http_err}"}}', 500)
        except Exception as err:
            logger.debug(f'An error occurred: {err}')
            return CustomResponse(f'{{"error": "An error occurred: {err}"}}', 500)



# Example usage:
# client = ApiClient()
# client.auth(1)
# response = client.doReq('get', '/some-operation')




class CustomResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code