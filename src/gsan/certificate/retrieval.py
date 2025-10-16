"""SSL certificate retrieval and context configuration."""

import socket
import ssl

from OpenSSL import crypto


def allow_unsigned_certificate() -> ssl.SSLContext:
    """Create an SSL context that allows unsigned certificates.

    Returns:
        SSL context configured to accept self-signed and unsigned certificates.

    """
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def get_certificate(
    hostname: str, port: int, timeout: float, context: ssl.SSLContext
) -> crypto.X509:
    """Retrieve X.509 certificate from a hostname and port.

    Args:
        hostname: Target hostname or IP address.
        port: Target port number.
        timeout: Connection timeout in seconds.
        context: SSL context for certificate validation.

    Returns:
        X.509 certificate object.

    Raises:
        ValueError: If certificate retrieval fails or no certificate is received.

    """
    try:
        with (
            socket.create_connection((hostname, port), timeout=timeout) as sock,
            context.wrap_socket(sock, server_hostname=hostname) as ssl_sock,
        ):
            cert = ssl_sock.getpeercert(binary_form=True)
            if cert is None:
                msg = f"No certificate received from {hostname}"
                raise ValueError(msg)
            x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, cert)
            return x509
    except Exception as e:
        msg = f"SSL certificate retrieval failed for {hostname}: {e!s}"
        raise ValueError(msg) from e
