from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
from pathlib import Path
import os.path


# convert .pfx to .pem and get path to correct certificates
def pfx2pem(pfx_path, pfx_password):
    if type(pfx_password) != str:
        raise TypeError("'pfx_password' must be a str")
    if type(pfx_path) != str:
        raise TypeError("'pfx_path' must be a str")
    # verify if certificate.pfx exists
    if not os.path.isfile(pfx_path):
        raise FileNotFoundError(f"'{pfx_path}' does not exist")
    if not os.path.exists(pfx_path.replace('.pfx', '.pem')):
        try:
            pfx = Path(pfx_path).read_bytes()
            private_key, main_cert, add_certs = load_key_and_certificates(
                pfx, pfx_password.encode('utf-8'), None)
            file_name = pfx_path.replace(
                'certificates/', '').replace('.pfx', '')
            with open(f'certificates/{file_name}.pem', 'w') as t_pem:
                with open(t_pem.name, 'wb') as pem_file:
                    pem_file.write(private_key.private_bytes(
                        Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
                    pem_file.write(main_cert.public_bytes(Encoding.PEM))
                    for ca in add_certs:
                        pem_file.write(ca.public_bytes(Encoding.PEM))
                return pem_file.name
        except ValueError as e:
            raise ValueError(f"invalid password for '{pfx_path}'")

    else:
        return pfx_path.replace('.pfx', '.pem')

print(pfx2pem('certificates/A1 - Contrutora Tenda - Matriz.pfx', '123456'))