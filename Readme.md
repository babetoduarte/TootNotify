# TootNotify

Python command line tool that lets you send **private** *Toots* (*i.e.* direct messages) to a mastodon user account.

``` bash
Send a Direct Message to someone on Mastodon!

Usage:

  python toot_notify.py -m <message_in_quotes> -r <@user@instance>

options:
  -h, --help            Show this help message and exit
  -r <@user@instan.ce>, --recipient <@user@instan.ce>
                        User who will receive a direct message.
  -m <message_body>, --message <message_body>
                        Body of the message to be sent.
  -s <spoiler_description>, --spoiler <spoiler_description>
                        Description for the spoiler warning which hides the message.
  -f <path_to_media_file [...]> [<path_to_media_file [...]> ...], --files <path_to_media_file [...]> [<path_to_media_file [...]> ...]
                        List of up to 4 media files to attach to the message.
  -x, --sensitive       Flag post/media as sensitive content (blur media)
  -v, --verbose         Print out verbose messages
  --version             show program's version number and exit

```

Make sure to put your credentials in a file called `credentials.py`, within the following variables:

```python
# Instance url (e.g. https://mastodon.social)
api_base_url = ""
# API Client Key
client_id = ""
# API Client Secret
client_secret = ""
# API Access Token
access_token = ""
# Default recipient for the private toots (e.g. @account@mastodon.social)
DEFAULT_RECIPIENT=""
```
