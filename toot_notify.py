#!/usr/bin/env python3

from credentials import *
from mastodon import Mastodon
from sys import argv, exit, stdout
from time import sleep
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

    # Argument for a list of attached media (image, video, audio only!)
    parser.add_argument(
        "-f",
        "--files",
        metavar="<path_to_media_file>",
        type=str,
        nargs='+',
        default=None,
        help="List of up to 4 media files to attach to the message.",
    )

    # Argument for flagging post/media as sensitive content
    parser.add_argument(
        "-x", "--sensitive",
        action="store_true",
        help="Flag post/media as sensitive content (blur media)"
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


    # If only one media file is passed into the script, make sure it gets
    # converted into a dictionary containing the single path of the media file
    if isinstance(args.files, str):
        post_media = [args.files]
    # Else, the default argparse argument will chain all elements into a list
    # of strings, containing the paths to the attached files
    else:
        post_media = args.files

    # Make sure the number of attached files does not exceed the maximum number
    # of attached images for Mastodon: maximum 4 images!
    if not len(post_media) <= 4:
        print(f"WARNING: the numer of attached media exceeds the maximum allowed per post (4)\n\tOnly adding the first four files!")
        post_media = post_media[:4]

    # If verbose, print the recipient, message and spoiler text
    if args.verbose:
        print(f"\tRECIPIENT: {args.recipient}\n\tMESSAGE: {args.message}\n\tSPOILER: {args.spoiler}\n\tMEDIA: {post_media}\n\tSENSITIVE: {args.sensitive}")

    # TODO: Make sure that media attachments follow these rules:
    # 1. Attached media consists of only images (Maximum 4!), or [DONE]
    # 2. Attached media consists of only ONE audio file, or
    # 3. Attached media consists of only ONE video file
    # TODO: Try/catch exceptions, report success/failure before exiting!
    send_toot(message=args.message, user=args.recipient, spoiler=args.spoiler,
              media=add_media(post_media), sensitive=args.sensitive)

    # Exit cleanly
    exit(0)


def check_media_upload(media_id_dict):
    ready = False
    status = mastodon.media_update(media_id_dict["id"])
    if status['url'] != None:
        ready = True
    return ready

def upload_wait(filename, media_id_dict, seconds=20, max_wait=30):
    print(f"Uploading file: {filename} with ID: {media_id_dict['id']}")
    success = False
    timeout = False
    elapsed = 1
    while (not success) and (not timeout):
        stdout.write("\r")
        stdout.write("{:2d}s elapsed.".format(elapsed))
        stdout.flush()
        if check_media_upload(media_id_dict):
            print("\nUpload successful!")
            success = True
        sleep(1)
        elapsed += 1
        if elapsed == max_wait:
            print("Upload timed out!")
            timeout = True

    return success


def add_file(media_file, description=None, sync=False):
    media_dict = None
    try:
        media_dict = mastodon.media_post(media_file, description=description,
                                         synchronous=sync)
    except Exception as e:
        print(f"ERROR: Could not determine added file's MIME type!\nMastodon only supports image, video, or audio files.\n\tERROR: {e}")
        print(f"WARNING: Could not add media {media_file}!")

    try:
       upload_wait(media_file, media_dict)
    except Exception as e:
        print(f"ERROR: {e}")

    return media_dict


def add_media(media_files):
    media_ids = []
    for media_file in media_files:
        media_ids.append(add_file(media_file))

    if not media_ids:
        media_ids = None

    return media_ids

def send_toot(message, user=DEFAULT_RECIPIENT, spoiler=None, media=None, sensitive=False):
    status_message = f"{user}\n {message}"
    mastodon.status_post(status=status_message,
                         visibility='direct',
                         media_ids=media,
                         spoiler_text=spoiler,
                         sensitive=sensitive)


if __name__ == '__main__':
    try:
        main(argv)
    except IndexError:
        print("No message argument provided!")
        exit(1)
