from multiprocessing.pool import Pool
from multiprocessing import freeze_support
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

    # Open payload json file
    if os.path.isfile(f'app/{consult_type}_payload.json'):
        try:
            with open(f'app/{consult_type}_payload.json') as json_file:
                data = json.load(json_file)
        except Exception as e:
            raise OSError(
                f"cannot open '{consult_type}_payload.json' because: {e}")
    else:
        raise OSError(f"'{consult_type}_payload.json' not found file")

    # requests from cte and search for CNPJ value in HTML document
    try:
        payload = data | {
            'ctl00$ContentPlaceHolder1$txtChaveAcessoResumo': code}
        cookies = {
            "AspxAutoDetectCookieSupport": "1"} if consult_type == 'nfe' else None
        req = requests.Session().post(
            f'https://www.{consult_type}.fazenda.gov.br/portal/consultaRecaptcha.aspx', data=payload, cookies=cookies)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise SystemExit(f'ERROR in {code}: {e}')
    try:
        # try capture parcial cnpj from html document
        if consult_type == 'cte':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find(
                "div", {"class": "wID25 pID_R10"}).find('p').getText()
            return [code, result[7:10]]
        elif consult_type == 'nfe':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find('td', {'class': 'col-5'}).find('span').getText()
            return [code, result[7:10]]
    except Exception as es:
        if str(es) == "'NoneType' object has no attribute 'find'":
            return f"Error in {code} CNPJ não encontrado"


# run multiple processes same time with different parameters
def multi_task(data_list):
    with Pool()as p:
        return p.starmap(get_cnpj, code_list)
