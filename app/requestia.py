from multiprocessing import Pool, freeze_support
import requests
import json
import re
import os


# change "yourdomain" to your domain name
domain = 'yourdomain'
# Login with your Requestia credentials,
with requests.Session() as session:
    with open('app/requestia/login_payload.json', 'r') as json_file:
        login = json.load(json_file)
        json_file.close()
    session.post(f'https://requestia.{domain}.com/services/authentication/Authentication.ashx/LogOn', data=login)


# get details of call
def get_details(call):
    details = session.post(f'https://requestia.{domain}.com/services/sm/Request.ashx/GetView', json={
                           "request": call, "requestContext": "2"}, headers={'Content-Type': 'application/json'}).text
    if "Material e Conhecimento de Transporte" in details:
        return call


# get details of some calls
def multi_details(call_list):
    with Pool() as p:
        all_calls = p.map(get_details, call_list)
        return [call for call in all_calls if call is not None]


# get pdf files attached on call
def get_pdf(call):
    files = session.post(f'https://requestia.{domain}.com/services/sm/Request.ashx/GetAttachments',
                         json={"requestId": call, "context": 2}, headers={'Content-Type': 'application/json'}).text
    pdf_list = [pdf for pdf in (re.findall(
        '"([^"]*)"', files)) if ".pdf" in pdf]
    return {call: pdf_list}


# get pdf files attached on some calls
def multi_pdf(valid_calls):
    with Pool() as p:
        call_pdfs = []
        dicts_list = p.map(get_pdf, valid_calls)
        for dicts in dicts_list:
            call_pdfs.append(dicts)
        return call_pdfs


# download files from every call in list
def download_files(call_pdf):
    for call, files in call_pdf.items():
        if not os.path.isdir(f'files/processing/{call}'):
            path = os.path.join('files/processing', call)
            os.mkdir(path)
        for pdf in files:
            try:
                if not os.path.exists(f'files/processing/{call}/{pdf}'):
                    print(f'downloading {call}: {pdf}')
                    with session.post(f'https://requestia.{domain}.com/services/sm/upload.ashx/DownloadAttachment', stream=True, data={"request": {call}, "blobName": pdf}) as r:
                            try:
                                with open(f'files/processing/{call}/{pdf}', 'wb') as f:
                                    for chunk in r.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            except Exception as e:
                                print(f'ERROR when download: {pdf}')
            except Exception as e:
                print(f'Error downloading file on call {call} - {pdf}: {e}') 

def multi_download_files(call_pdfs):
    with Pool() as p:
        p.map(download_files, call_pdfs)

# get calls
def main_requestia():
    result = session.post(f'https://requestia.{domain}.com/services/sm/inbox.ashx/GetInboxGrid', json={
                          "params": {"context": 2, "limit": 500}}, headers={'Content-Type': 'application/json'}).text
    result += session.post(f'https://requestia.{domain}.com/services/sm/inbox.ashx/GetInboxGrid', json={
                           "params": {"context": 4, "limit": 500}}, headers={'Content-Type': 'application/json'}).text
    call_list = [item for item in (re.findall(
        '"([^"]*)"', result)) if "TND" in item]
    valid_calls = multi_details(call_list)
    call_pdfs = multi_pdf(valid_calls)
    multi_download_files(call_pdfs)

if __name__ == "__main__":
    if os.name == 'nt':
        freeze_support()
    main_requestia()