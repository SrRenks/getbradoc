from bs4 import BeautifulSoup
import tempfile
import os


# read the xml file and return data
def read_xml(filename):
    if type(filename) != str:
        raise TypeError('filename must be a string')
    if os.path.isfile(f'tmp/{filename}'):
        with open(f'tmp/{filename}', 'r') as f:
            xml_data = BeautifulSoup(f.read(), "xml")
        consult_type = filename[0:3]
        nota = xml_data.find(f'ch{consult_type[0:2].upper() + consult_type[2:].lower()}').getText()
        serie = xml_data.find('serie').getText()
        data_emissao = xml_data.find('dhEmi').getText()
        emitente = xml_data.find('emit').find('CNPJ').getText()
        destinatario = xml_data.find('dest').find('CNPJ').getText()
        vencimento = xml_data.find('dVenc').getText()
        total = xml_data.find(f'v{consult_type[0:2].upper()}').getText()
        os.unlink(f'tmp/{filename}')
        return (nota, serie, data_emissao, emitente, destinatario, vencimento, total)
    else:
        raise OSError(f"'tmp/{filename}' not found file")
