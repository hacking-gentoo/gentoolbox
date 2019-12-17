# Copyright(c) 2009, Gentoo Foundation
# Copyright(c) 2019, MAD Hacking
#
# Licensed under the GNU General Public License, v2

"""Display all keywords for a given package converting to masked as unstable"""

# =======
# Imports
# =======

import sys
from getopt import gnu_getopt, GetoptError

import gentoolkit.pprinter as pp
from gentoolkit import errors
from gentoolkit.equery import format_options, mod_usage, CONFIG
from gentoolkit.query import Query

# =======
# Globals
# =======

# =========
# Functions
# =========

def print_help(with_description=True):
    """Print description, usage and a detailed help message.
    @type with_description: bool
    @param with_description: if true, print module's __doc__ string
    """

    if with_description:
        print(__doc__.strip())
        print()
#    print("Default depth is set to 1 (direct only). Use --depth=0 for no max.")
#    print()
    print(mod_usage(mod_name="maskedkeywords"))
    print()
    print(pp.command("options"))
    print(format_options((
        (" -h, --help", "display this help message"),
    )))


def parse_module_options(module_opts):
    """Parse module options and update QUERY_OPTS"""

    opts = (x[0] for x in module_opts)
    for opt in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)


def main(input_args):
    """Parse input and run the program"""

    short_opts = "h"
    long_opts = ('help')

    try:
        module_opts, queries = gnu_getopt(input_args, short_opts, long_opts)
    except GetoptError as err:
        sys.stderr.write(pp.error("Module %s" % err))
        print()
        print_help(with_description=False)
        sys.exit(2)

    parse_module_options(module_opts)

    if not queries or len(queries) > 1:
        print_help()
        sys.exit(2)

    #
    # Output
    #

    query = Query(queries[0])

    matches = query.find(include_masked=True, in_installed=False)

    if not matches:
        raise errors.GentoolkitNoMatches(query)

    matches.sort()
    matches.reverse()
    
    if CONFIG['verbose']:
        print(matches[0].ebuild_path())
        print()
    
    ebkw = matches[0].environment('KEYWORDS')
    uskw = []
    
    for kw in ebkw.split():
        if kw[0] != '-' and kw[0] != '~':
            uskw.append('~' + kw)
        else:
            uskw.append(kw)
    
    print(' '.join(uskw))
    


if __name__ == '__main__':
    main(sys.argv)

