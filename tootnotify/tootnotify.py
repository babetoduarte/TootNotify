#!/usr/bin/env python3
"""
       TootNotify - Send DMs to a Mastodon Account from the Command Line!
                     Copyright (C) 2023  Jorge A. Duarte G.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.

                                      ===

TootNotify - Version 1.0.0-RC1
by: Jorge A. Duarte - babetoduarte@gmail.com
July 11, 2023

This is a python command line utility, which is able to send direct messages to
a provided user on Mastodon. To use this tool you will need to have a Mastodon
API application created, with its corresponding API credentials. You will also 
need to store these credentials in configuration file called '.tootnotifyrc' in
your $HOME directory, as TootNotify expects to find this file using the path:

    $HOME/.tootnotifyrc

By default, the '.tootnotifyrc' file is not shipped with the project, and must
be created by the user, populating the required variables for API access in the
following format:

    [tootnotify]
    # Instance url (e.g. https://mastodon.social)
    api_base_url = YOUR_INSTANCE_URL
    # API Client Key
    client_id = YOUR CLIENT_ID
    # API Client Secret
    client_secret = YOUR_CLIENT_SECRET
    # API Access Token
    access_token = YOU_ACCESS_TOKEN
    # Default recipient for the private toots (e.g. @account@mastodon.social)
    DEFAULT_RECIPIENT = YOUR_DEFAULT_RECIPIENT

Make sure that the first line and all variable names are copied verbatim into 
your configuration file. Among the variables, a DEFAULT_RECIPIENT can be
configured, so that when using TootNotify systematically to notify the same
user, the recipient address doesn't have to be provided every time.

"""
import argparse
from configparser import ConfigParser
from pathlib import Path
from sys import argv, exit, stdout
from time import sleep

from mastodon import Mastodon

# Read the user's configuration file stored in (~/.tootnotifyrc)
# Instantiate a configutation parser
config = ConfigParser()
# Try to read the configuration file
try:
    # Make sure to safely open the configuration file
    with open(f"{Path.home()}/.tootnotifyrc") as f:
        # Read the configuration properties
        config.read_file(f)
# If no configuration file is found
except IOError:
    # Notify the user
    print(f"ERROR: No config file ~/.tootnotifyrc found!")
    # And exit with a non-zero status
    exit(2)

# Variables that are read in from the configuration file
# Instance URL
api_base_url = config['tootnotify']['api_base_url']
# API Client Key
client_id = config['tootnotify']['client_id']
# API Client Secret
client_secret = config['tootnotify']['client_secret']
# API Access Token
access_token = config['tootnotify']['access_token']
# Default recipient for the private toots
DEFAULT_RECIPIENT = config['tootnotify']['DEFAULT_RECIPIENT']

# Setup the Mastodon API credentials and access, using the values imported from
# the '~/.tootnotifyrc' file within the users $HOME folder.
mastodon = Mastodon(client_id,
                    client_secret,
                    access_token,
                    api_base_url)

def main(argv):
    """Main function of the program, which runs when TootNotify is invoked.
    """
    # Define the parser for handling the arguments passed into the script, as
    # well as the built-in documentation for the --help/-h argument using the
    # argparse library included in Python.
    parser = argparse.ArgumentParser(
        # Name of the program
        prog="tootnotify",
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
        help="Flag post/media as sensitive content (blur media)."
    )

   # Argument for media upload timeout
    parser.add_argument(
        "-t",
        "--timeout",
        metavar="<timeout_in_seconds>",
        type=int,
        default=30,
        help="Number of seconds to wait for a single media file to upload.",
    )

    # Argument for verbose output and print-outs
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print out verbose messages."
    )

    # Argument for printing out the current version of this script
    parser.add_argument(
        "--version", action="version", version="%(prog)s v1.0.0-RC1 [07/12/2023]"
    )

    # Parse arguments passed into the main function
    args = parser.parse_args()

    # Global constant which colds the verbose flag
    VERBOSE = args.verbose

    # If verbose, print out the arguments Namespace() object
    if VERBOSE:
        print(f"ARGV: {args}")


    # If only one media file is passed into the script, make sure it gets
    # converted into a dictionary containing the single path of the media file
    if isinstance(args.files, str):
        post_media = [args.files]
    # Else, the default argparse argument will chain all elements into a list
    # of strings, containing the paths to the attached files
    elif isinstance(args.files, list):
        post_media = args.files
    else:
        post_media = []

    # Make sure the number of attached files does not exceed the maximum number
    # of attached images for Mastodon: maximum 4 images!
    if not len(post_media) <= 4:
        print(f"WARNING: the numer of attached media exceeds the maximum "
              f"allowed per post (4). Only adding the first four files!")
        post_media = post_media[:4]


    # If verbose, print the recipient, message and spoiler text
    if VERBOSE:
        print(f"\tRECIPIENT: {args.recipient}\n\tMESSAGE: {args.message}\n\t"
              f"SPOILER: {args.spoiler}\n\tMEDIA: {post_media}\n\t"
              f"SENSITIVE: {args.sensitive}\n\tTIMEOUT: {args.timeout}s")

    # TODO: Make sure that media attachments follow these rules:
    # 1. Attached media consists of only images (Maximum 4!), or [DONE]
    # 2. Attached media consists of only ONE audio file, or
    # 3. Attached media consists of only ONE video file
    toot = send_toot(message=args.message, user=args.recipient,
                     spoiler=args.spoiler,
                     media=add_media(post_media, args.timeout, VERBOSE),
                     sensitive=args.sensitive)

    # Exit cleanly
    if toot:
        # If verbose, inform of success
        if VERBOSE:
            print("SUCCESS: Toot sent succesfully!")
        exit(0)
    else:
        # If verbose, inform of failure
        if VERBOSE:
            print("FAIL: Failed to send Toot!")
        exit(1)


def check_media_upload(media_id_dict, verbose=False):
    """ Check if the upload of a media file has completed.

    This function receives a media_id dictionary, and checks the "id" key's
    contents to determine whether the media upload has been completed. A
    completed media upload has a valid URL associated to the "url" key. This
    function returns a boolean 'ready' variable that indicates whether an
    upload has completed or not.
    """
    # Default return value
    ready = False

    # Get the id for the media being uploaded
    media_id = media_id_dict["id"]

    # Get a status update on the media being uploaded, by retrieving an updated
    # media_id dictionary using the ID of the media_id dictionary in question
    try:
        # If verbose, inform the user of the media_id status retrieval
        if verbose:
            print(f"Retrieving status update for media id: {media_id}")
        status = mastodon.media_update(media_id)
    # If an exception occurs, print it out, and set status to None
    except Exception as e:
        print(f"API ERROR: Could not verify media update!\n\t{e}")
        status = None

    # If the status's URL is not None, return a true value
    if status['url'] != None:
        ready = True

    # Return the check outcome
    return ready


def upload_wait(filename, media_id_dict, max_wait=30, verbose=False):
    """Wait for a media upload to finish, up to max_wait seconds (30s)

    This function receives a media_id dictionary, checks if its corresponding
    media upload is completed, and if not, it waits up to max_wait (30) seconds,
    before returning a boolean 'success' variable.
    """
    # If verbose, inform the user of the file upload
    if verbose:
        print(f"Uploading file: {filename} with ID: {media_id_dict['id']}")

    # Default return value
    success = False
    # Timeout assessment variable
    timeout = False
    # Time counter (seconds)
    elapsed = 0

    # Waiting loop to check for media upload to complete
    # While no upload confirmation has been received, and we have not exceeded
    # the defined timeout in seconds
    while (not success) and (not timeout):
        # If verbose, show the waiting time elapsed
        if verbose:
            stdout.write("\r")
            stdout.write("{:2d}s elapsed.".format(elapsed))
            stdout.flush()

        # If the media has uploaded successfully
        if check_media_upload(media_id_dict):
            #If verbose, inform that the media was uploaded successfully
            if verbose:
                print("\nUpload successful!")
            # Change the return value to True
            success = True
        # If we're still waiting for the media to be uploaded
        else:
            # Wait for 1 second
            sleep(1)
            # Increase the time counter
            elapsed += 1

        # If the elapse time is equal to the maximum wait time defined
        if elapsed == max_wait:
            # If verbose, inform that the upload timed out!
            print(f"\nERROR: Upload timed out!"
                  f"Proceeding with the Toot, but your media may not be there.")
            # Set the timeout variable to True
            timeout = True

    # Return the success value
    return success


def add_file(media_file, description=None, sync=False,
             timeout=30, verbose=False):
    """ Add a media file to Mastodon, to be attached to a Toot.

    This function uploads a media file to Mastodon, and then awaits for a
    confirmation from the API that the media file was received. Once confirmed,
    it returns the update media dictionary for the uploaded file.
    """
    # Output Mastodon media dictionary
    media_dict = None

    # Try to upload a media file using the API to get back a media dict
    try:
        # Upload file to Mastodon, and receive a media_dict object as a response
        media_dict = mastodon.media_post(media_file, description=description,
                                         synchronous=sync)

        # Try to wait for the upload of the file to finish
        try:
            # Wait for the upload to finish
            upload_wait(media_file, media_dict, timeout, verbose)
        # If any exception is raised, notify the user of the error
        except Exception as e:
            print(f"ERROR: {e}")
            # If verbose, inform the user about the file not bein uploaded
            if verbose:
                print(f"WARNING: Could not confirm the media was uploaded! ")
    # Catch any exception, and notify the user of the error
    except Exception as e:
        print(f"ERROR: Could not determine added file's MIME type!\nMastodon only supports image, video, or audio files.\n\tERROR: {e}")
        # If verbose, print warning explaining which file could not be uploaded
        if verbose:
            print(f"WARNING: Could not add media {media_file}! "
                  f"Proceeding with the Toot, but your media won't be there!")

    # Return the media dictionary of the uploaded file
    return media_dict


def add_media(media_files, timeout=30, verbose=False):
    """ Add one or more media files to Mastodon, to be attached to a Toot.

    This function iteratively uploads media files to Mastodon, and awaits for
    confirmations from the API that each media file was received, before
    proceeding to upload the next media file. When done, it returns a list of
    media_id dictionaries returned by the API (one for each media file).
    """
    # Output list of media IDs
    media_ids = []

    # Iterate over each media file
    for media_file in media_files:
        # Upload the media file to Mastodon, and append the resulting media_id
        # dictionary to the output list
        media_ids.append(add_file(media_file, timeout=timeout, verbose=verbose))

    # If no media IDs are returnes (empty media_ids list)
    if not media_ids:
        # Return None instead of an empty list
        media_ids = None

    # Return the output list of media IDs, or None
    return media_ids


def send_toot(message, user=DEFAULT_RECIPIENT,
              spoiler=None, media=None, sensitive=False,
              verbose=False):
    """Function that sends a private Toot to a recipient.

    This function sends a private Toot to a defined recipient, including any
    provided media files (list of paths to none, one, or more files), and if
    desired, the Toot can be flagged as containing sensitive content, as well as
    a spoiler/content warning can be added. This function returns a boolean
    value depending on whether sending the Toot (with or without media, in case
    the upload fails) was successful or not.
    """
    # Default output variable
    success = False

    # Construct the status message for the Toot, make sure it is a Direct
    # Message by mentioning the recipient first, and then attaching the content
    # of the message below the mention. Also, post the Toot with visibility set
    # to 'direct'.
    status_message = f"{user}\n {message}"

    # Try to sent the Toot
    try:
        # Compose and sent the Toot including any media, spoiler text, and flag
        # for sensitive content or not
        mastodon.status_post(status=status_message,
                             visibility='direct',
                             media_ids=media,
                             spoiler_text=spoiler,
                             sensitive=sensitive)

        # If succesfull, change default output variable to True
        success = True
    # If something goes wrong sending the Toot
    except Exception as e:
        # Catch and show the exception
        print(f"ERROR: {e}")

        # Make sure the default output variable is set to False
        success = False

    # Return whether the posting was successful or not
    return success


def run_cli():
    exit(main(argv))


# If this script is executed from the command line
if __name__ == '__main__':
    # Try to run main() function with the provided arguments
    main(argv)
