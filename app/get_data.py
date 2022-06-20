from app.send_email import expiration_coming
from multiprocessing import freeze_support
from datetime import datetime, timedelta
from app.pfx2pem import pfx2pem
from shutil import copyfileobj
from bs4 import BeautifulSoup
import requests
import os.path
import json
import os


# get parcial cnpj value from CTE/NFE
def get_data(code, consult_type):
    if type(code) not in [str, int]:
        raise TypeError('code must be a string or int')
    if type(consult_type) != str:
        raise TypeError('consult_type must be a string')
    if consult_type not in ['cte', 'nfe']:
        raise AttributeError("valid consult_types: 'cte', 'nfe'")

    # find payload json file and set cookies
    if os.path.isfile(f'app/{consult_type}_payload.json'):
        with open(f'app/{consult_type}_payload.json') as json_file:
            data = json.load(json_file)
        payload = data | {'ctl00$ContentPlaceHolder1$txtChaveAcessoResumo': code}
        cookies = {"AspxAutoDetectCookieSupport": "1"} if consult_type == 'nfe' else None
    else:
        raise OSError(f"'{consult_type}_payload.json' not found file")

    # requests from CTE/NFE HTML document and save session cookie
    try:
        session = requests.Session()
        req = session.post(f'https://www.{consult_type}.fazenda.gov.br/portal/consultaRecaptcha.aspx', data=payload, cookies=cookies)
    except requests.exceptions.RequestException as e:
        raise SystemExit(f'ERROR in {code}: {e}')

    # try capture parcial CNPJ from html document
    try:
        if consult_type == 'cte':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find("div", {"class": "wID25 pID_R10"}).find('p').getText()
            parcial_cnpj = result[7:10]
        elif consult_type == 'nfe':
            soup = BeautifulSoup(req.content, "html.parser")
            result = soup.find('td', {'class': 'col-3'}).find('span').getText()
            parcial_cnpj = result[7:10]
    except Exception as es:
        if str(es) == "'NoneType' object has no attribute 'find'":
            with open(f'logs/error_{code}.html', 'w') as r:
                r.write(req.text)
            raise AttributeError(
                f"ERROR in {code}: data not found, check file '{consult_type}_payload.json' and request HTML page.")
        else:
            raise SystemExit(f'ERROR in {code}: {es}')

    # search for the certificate for the partial CNPJ in custom certificates.json, if not found, select the default.
    if os.path.isfile('certificates/custom_certificates.json'):
        with open('certificates/custom_certificates.json') as custom_list:
            pfx_data = custom_list[parcial_cnpj] if parcial_cnpj in custom_list else ["certificates/A1 - Contrutora Tenda - Matriz.pfx", "123456"]
            pem, expiration = pfx2pem(pfx_data[0], pfx_data[1])
            remaining_days = (expiration - datetime.now()).days
            expiration_date = expiration.strftime('%d/%m/%Y')
            if remaining_days <= 5:
                expiration_coming(pem, remaining_days, expiration_date)
    else:
        raise OSError(f"'custom_certificates.json' not found file")

    # try download XML File
    try:
        # try open download_payload.json to get payload data for request
        if os.path.isfile('certificates/custom_certificates.json'):
            with open(f'app/download_payload.json') as json_file:
                payload = json.load(json_file)
        else:
            raise OSError(f"'custom_certificates.json' not found file")
        # try download
        with session.post(req.url, stream=True, data=payload) as r:
            with session.get(r.url, cert=pem, stream=True) as file:
                with open(f"tmp/{consult_type}{code}.xml", 'wb') as outfile:
                    copyfileobj(file.raw, outfile)
                    outfile.close()
        # checks if the xml file has more than one line, as it is an error signal
        with open(f'tmp/{consult_type}{code}.xml', 'rb') as xml_file:
            lines = [i for i in xml_file.readlines() if len(i)>1]
            if len(lines) > 1 or len(lines) == 0:
                xml_file.close()
                if not os.path.exists(f'logs/error_{consult_type}{code}.xml'):
                    os.rename(f'tmp/{consult_type}{code}.xml', os.path.join('logs/', f'error_{consult_type}{code}.xml'))
                else:
                    os.unlink(f'tmp/{consult_type}{code}.xml')
                print(F"'tmp/{consult_type}{code}.xml' contains unexpected error, moved to logs")
            else:
                xml_file.close()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f'ERROR in {code}: {e}')
