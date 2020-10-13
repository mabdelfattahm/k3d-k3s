import schedule
from argparse import ArgumentParser, ArgumentTypeError
from random import choice
from re import compile
from string import ascii_letters
from subprocess import Popen, PIPE

def encode_password(pw_str: str, method: str = "sha-512") -> str:
    """ Encode given string password using mkpasswd
        and sha-512 as a default encryption method
        and return a string
    """
    p = Popen(
        f"mkpasswd -m {method} {pw_str}",
        shell=True, stdout=PIPE, stderr=PIPE
    )
    (out, err) = (p.out, p.err)
    err_str = err.stdoud.read().strip().decode("UTF-8")
    if err_str:
        raise ValueError(err_str)
    return p.stdout.read().strip().decode("UTF-8")

def generate_password(length: int = 16) -> str :
    """ Generate new password with the given length """
    return ''.join(choice(ascii_letters) for _ in range(length))

def update_config(pwd: str) -> bool:
    return False

def notify(mail: str, pwd: str) -> None:
    return

def job(mail: str) -> None:
    pwd = encode_password(generate_password())
    if update_config(pwd):
        notify(mail, pwd)

def create_scheduler(refresh: int, mail: str) -> None: 
    schedule.every(refresh).days.do(job, mail)

def check_days(value: int) -> int:
    iv = int(value)
    if iv <= 0 or iv > 365: 
        raise ArgumentTypeError(
            f"{value} is an invalid value .. it must be between 1 and 365"
        )
    return iv

def check_mail(value: str) -> str:
    pat = compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if not pat.match(value) : 
        raise ArgumentTypeError(f"{value} is not a valid email string")
    return value

def argparser() -> ArgumentParser:
    parser = ArgumentParser(
        usage="%(prog)s [OPTION] [REFRESH] [MAIL]",
        description="Generate and rotate passwords with email notification."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument(
        "refresh", nargs=1, type=check_days,
        help="Number of days after which the password should be updated"
    )
    parser.add_argument(
        "mail", nargs=1, type=check_mail, 
        help="Email to which the change notification will be sent"
    )
    return parser

def main():
    args = argparser().parse_args()
    print(f"mail: {args.mail}, refresh: {args.refresh} days")
    try :
        create_scheduler(args.refresh, args.mail)
        while True:
            schedule.run_pending()
    except ValueError as err:
        print(err)

if __name__ == "__main__":
    main()
    