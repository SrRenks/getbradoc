from multiprocessing.pool import Pool
from multiprocessing import freeze_support
from pfx2pem import pfx2pem
from bs4 import BeautifulSoup
import requests
import os.path
import json
import os


# get parcial cnpj value from CTE/NFE
def get_cnpj(code, consult_type):
    if type(code) not in [str, int]:
        raise TypeError('code must be a string or int')
    if type(consult_type) != str:
        raise TypeError('consult_type must be a string')
    if consult_type not in ['cte', 'nfe']:
        raise AttributeError("valid consult_types: 'cte', 'nfe'")

    # find payload json file and set cookies
    if os.path.isfile(f'app/{consult_type}_payload.json'):
        try:
            with open(f'app/{consult_type}_payload.json') as json_file:
                data = json.load(json_file)
            payload = data | {
                'ctl00$ContentPlaceHolder1$txtChaveAcessoResumo': code}
            cookies = {
                "AspxAutoDetectCookieSupport": "1"} if consult_type == 'nfe' else None
        except Exception as e:
            raise OSError(
                f"cannot open '{consult_type}_payload.json' because: {e}")
    else:
        raise OSError(f"'{consult_type}_payload.json' not found file")
    # requests from CTE/NFE HTML document and save session cookie
    try:
        req = requests.Session().post(
            f'https://www.{consult_type}.fazenda.gov.br/portal/consultaRecaptcha.aspx', data=payload, cookies=cookies)
        session_cookie = dict(req.history[0].cookies)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(f'ERROR in {code}: {e}')
    # try capture parcial CNPJ from html document
    try:
        if consult_type == 'cte':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find(
                "div", {"class": "wID25 pID_R10"}).find('p').getText()
            parcial_cnpj = result[7:10]
        elif consult_type == 'nfe':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find('td', {'class': 'col-3'}).find('span').getText()
            parcial_cnpj = result[7:10]
    except Exception as es:
        if str(es) == "'NoneType' object has no attribute 'find'":
            with open('test.html', 'w') as r:
                r.write(req.text)
            raise SystemExit(
                f"ERROR in {code}: data not found, check file '{consult_type}_payload.json' and request HTML page.")
        else:
            raise SystemExit(f'ERROR in {code}: {es}')
    # request to CTE/NFE to get full data of the cod
    try:
        #payload for download link
        payload = {
        "tipoConsulta": "resumo",
        "a": "IXO2fKs9zGK04lBhkURUHKerH8FB6LiqpXPKhRXt7L9nRvPre5vAFtOSkmHpUrhV",
        "tipoConteudo": "7PhJ gAVw2g=",
        "lp": "SVhPMmZLczl6R0swNGxCaGtVUlVIS2VySDhGQjZMaXFwWFBLaFJYdDdMOW5SdlByZTV2QUZyZDd4L1BtS1JvRXRsamJjeTdIQWJMSklrTTJISHFxdGQxSExoOTFEQVM1aVRjN2w1OW1DU0k90"}
        #get .pem certificates
        with open('certificates/custom_certificates.json') as custom_list:
            pfx_path = custom_list[parcial_cnpj] if parcial_cnpj in custom_list else "certificates/A1 - Contrutora Tenda - Matriz.pfx"
            pem, expiration = pfx2pem(pfx_path, "123456")
        #try download XML File
        with requests.Session().post(f"https://www.{consult_type}.fazenda.gov.br/portal/downloadNFe.aspx", cookies=session_cookie, stream=True, cert=pem) as r:
            r.raise_for_status()
            with open('test.xml', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(f'ERROR in {code}: {e}')
        
# run multiple processes same time with different parameters
def multi_task(data_list):
    with Pool()as p:
        return p.starmap(get_cnpj, data_list)
