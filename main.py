from multiprocessing import Pool, freeze_support
from app.get_data import get_data
from app.read_xml import read_xml
import os

def multi_get_data(data_list):
    with Pool() as p:
        p.starmap(get_data, data_list)


def multi_read_xml(path_list):
    with Pool() as p:
        return p.map(read_xml, path_list)

if __name__ == '__main__':
    if os.name == 'nt':
        freeze_support()
    data_list = [(35220564748494000170550010000026011909709830, 'nfe')]
    multi_get_data(data_list)
    print(multi_read_xml(next(os.walk('tmp'), (None, None, []))[2]))