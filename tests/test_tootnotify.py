#!/usr/bin/env python3
"""
       TootNotify - Send DMs to a Mastodon Account from the Command Line!
                     Copyright (C) 2023  Jorge A. Duarte G.

                                      ===

TootNotify - Version 1.0.0-RC1
by: Jorge A. Duarte - babetoduarte@gmail.com
July 11, 2023

This is a pytest test file for testing the functionality of TootNotify. For now
it only tests a single function. Future changes will implement new testing
capabilities, in order to provide coverage for as much of TootNotify's code as
possible.
"""

from tootnotify.tootnotify import check_media_file_list


def test_check_media_file_list():
    """ Test for the function test_check_media_file_list().

    This test makes sure that any given list passed as parameter to the
    check_media_file_list() is only up to 4 items long, or less.
    """
    test_list = ["a", "b", "c", "d", "e", "f", "g", "h"]
    result = check_media_file_list(test_list)
    assert len(result) <= 4
