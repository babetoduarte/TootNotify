#!/usr/bin/env python3

from credentials import *
from mastodon import Mastodon
from sys import argv, exit
import argparse


mastodon = Mastodon(client_id,
                    client_secret,
                    access_token,
                    api_base_url)

def main(argv):
    """Main function of the program."""
    # Define the parser for handling the arguments passed into the script
    parser = argparse.ArgumentParser(
        # Name of the program
        prog="toot_notify.py",
        # Description of the program
        description="Send a Direct Message to someone on Mastodon!",
        # Footnote that appears after the help dialog
        epilog="Developed by Jorge Duarte - babetoduarte@gmail.com",
    )

    # Argument for the message recipient
    parser.add_argument(
        "-r",
        "--recipient",
        metavar="<@user@instan.ce>",
        default=DEFAULT_RECIPIENT,
        help="User who will receive a direct message.",
    )

    # Argument for the message body
    parser.add_argument(
        "-m",
        "--message",
        metavar="<message_body>",
        default="Testing!",
        help="Body of the message to be sent.",
    )

    # Argument for the spoiler text warning
    parser.add_argument(
        "-s",
        "--spoiler",
        metavar="<spoiler_description>",
        default=None,
        help="Description for the spoiler warning which hides the message.",
    )

    # Argument for verbose output and print-outs
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print out verbose messages"
    )

    # Argument for printing out the current version of this script
    parser.add_argument(
        "--version", action="version", version="%(prog)s v1.0 [07/10/2023]"
    )

    # Parse arguments passed into the main function
    args = parser.parse_args()

    # If verbose, print out the arguments Namespace() object
    if args.verbose:
        print(f"ARGV: {args}")

    # If verbose, print the recipient, message and spoiler text
    if args.verbose:
        print(f"\tRECIPIENT: {args.recipient}\n\tMESSAGE: {args.message}\n\tSPOILER: {args.spoiler}")

    # Send private toot!
    # TODO: Add abiliti to attach media!
    # TODO: Try/catch exceptions, report success/failure before exiting!
    notify_me(message=args.message, user=args.recipient, spoiler=args.spoiler)

    # Exit cleanly
    exit(0)

def notify_me(message, user=DEFAULT_RECIPIENT, spoiler=None):
    status_message = f"{user}\n {message}"
    mastodon.status_post(status=status_message,
                         visibility='direct',
                         spoiler_text=spoiler)


if __name__ == '__main__':
    try:
        main(argv)
    except IndexError:
        print("No message argument provided!")
        exit(1)
