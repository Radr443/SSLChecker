from datetime import datetime
import socket
import ssl
from urllib.parse import urlparse
import termcolor
import sys
from colorama import init

init()
# Used to accept text files to read domains off 
def check_file(filename):
    try:
        with open(filename, "r") as file:
            domains = [
                line.strip()
                for line in file
                if line.strip()
            ]
        for domain in domains:
            check_ssl(domain)
    except FileNotFoundError:
        print(
            termcolor.colored(
                f"File not found: {filename}",
                "red"
            )
        )

def check_ssl(domain):
    if "://" not in domain:
        domain = "https://" + domain
    parsed = urlparse(domain)
    domain = parsed.netloc or parsed.path
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(
                sock,
                server_hostname=domain
            ) as ssock:
                cert = ssock.getpeercert()
                not_after = cert["notAfter"]
                time_parts = not_after.rsplit(' ', 1)[0]
                expiration_date = datetime.strptime(
                    time_parts,
                    "%b %d %H:%M:%S %Y"
                )
                days_remaining = (
                    expiration_date - datetime.now()
                ).days
                if days_remaining < 30:
                    print(
                        termcolor.colored(
                            f"{domain} expires in {days_remaining} days",
                            "yellow"
                        )
                    )
                else:
                    print(
                        termcolor.colored(
                            f"{domain} valid for {days_remaining} more days",
                            "green"
                        )
                    )
    except ssl.SSLCertVerificationError as e:
        if "expired" in str(e).lower():
            print(
                termcolor.colored(
                    f"Certificate for {domain} is expired",
                    "red"
                )
            )
        else:
            print(
                termcolor.colored(
                    f"SSL Error for {domain}: {e}",
                    "red"
                )
            )

    except Exception as e:
        print(
            termcolor.colored(
                f"Error checking {domain}: {e}",
                "light_grey"
            )
        )
# MAIN
try:

    while True:
        domains = input(
            "Enter domains manually supported by commas to search for multiple domains\nor provide a txt file with domains (ex: domains.txt OR example.com,example.org): "
        ).strip()
        if domains.endswith(".txt"):
            check_file(domains)
        else:

            domain_list = [
                d.strip()
                for d in domains.split(",")
            ]
            for domain in domain_list:
                check_ssl(domain)
        action = input(
            "Type check to scan again or anything else to exit: "
        )

        if action.lower() != "check":
            sys.exit(0)

except KeyboardInterrupt:

    print(
        "\nI didnt like you anyway "
        + termcolor.colored(":(", "red")
    )

    sys.exit(0)
