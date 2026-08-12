"""Generate a self-signed certificate pair used by the QUIC transport.

The aioquic server loads `certs/cert.pem` and `certs/key.pem`. These files are
git-ignored (a TLS private key must never be committed), so a fresh clone must
run this script once before starting the server:

    venv\\Scripts\\python certs\\generate_certs.py
"""
import datetime
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

HERE = Path(__file__).parent

CERT_PATH = HERE / "cert.pem"
KEY_PATH = HERE / "key.pem"

# The protocol demo disables client-side verification of the self-signed cert
# (agent/transport/client.py), so a CN is only used for identification.
SUBJECT = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "SPQ-A2A-Demo"),
])


def main():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    now = datetime.datetime.now(datetime.timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(SUBJECT)
        .issuer_name(SUBJECT)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    KEY_PATH.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    CERT_PATH.write_bytes(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Certificate written to {CERT_PATH}")
    print(f"Private key   written to {KEY_PATH}")


if __name__ == "__main__":
    main()