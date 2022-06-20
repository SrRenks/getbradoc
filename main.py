from multiprocessing import Pool, freeze_support
from app.get_data import get_data
from app.read_xml import read_xml
from app.read_pdf import read_pdf
import os


# multiprocessing for read_pdf
def multi_read_pdf(pdf_path):
    with Pool() as p:
        return p.map(read_pdf, pdf_path)


# multiprocessing for get_data
def multi_get_data(data_list):
    with Pool() as p:
        p.starmap(get_data, data_list)


# multiprocessing for read_xml
def multi_read_xml(path_list):
    with Pool() as p:
        return p.map(read_xml, path_list)


if __name__ == '__main__':
    # if run in Windows, freeze_support is available
    if os.name == 'nt':
        freeze_support()
    # path for pdf files
    pdf_list = []
    pdf_list.extend([os.path.join(".", file) for file in os.listdir(".") if file.endswith(".pdf")])
    # arguments for get_data
    data_list = multi_read_pdf(pdf_list)
    multi_get_data(data_list)
    # get data for all xml files
    xml_data = multi_read_xml(next(os.walk('tmp'), (None, None, []))[2])
