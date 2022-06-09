from multiprocessing.pool import Pool
from bs4 import BeautifulSoup
import requests
import os.path
import json


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
        req = requests.Session().post(f'https://www.{consult_type}.fazenda.gov.br/portal/consultaRecaptcha.aspx', data=payload, timeout=2)
    except requests.exceptions.Timeout as e:
        raise 
    try:
        # try capture parcial cnpj from html document
        if consult_type == 'cte':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find(
                "div", {"class": "wID25 pID_R10"}).find('p').getText()
            return [code, result[7:10]]
        elif consult_type == 'nfe':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find(
                "table", {"class": "box"})
            return [code, result, result[7:10]]
    except Exception as es:
        if str(es) == "'NoneType' object has no attribute 'find'":
            return f"Error in {code} CNPJ não encontrado"


# run multiple processes same time with different parameters
def multi_task(code_list):
    with Pool() as p:
        return p.starmap(get_cnpj, code_list)
