#!/usr/bin/python
#
# Copyright 2003-2004 Karl Trygve Kalleberg
# Copyright 2003-2009 Gentoo Foundation
# Copyright 2019      MAD Hacking
#
# Distributed under the terms of the GNU General Public License v2

"""Gentoolbox is a collection of development scripts for Gentoo"""

import sys

CONFIG = {
    # Color handling: -1: Use Portage settings, 0: Force off, 1: Force on
    'color': -1,
    # Guess piping output:
    'piping': False if sys.stdout.isatty() else True,
    # Set some defaults:
    'quiet': False,
    # verbose is True if not quiet and not piping
    'verbose': True,
    'debug': False
}
