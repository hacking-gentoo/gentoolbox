# Copyright(c) 2009, Gentoo Foundation
# Copyright(c) 2019, MAD Hacking
#
# Licensed under the GNU General Public License, v2

"""Display dependency spec for a given package"""

# =======
# Imports
# =======

import sys
from getopt import gnu_getopt, GetoptError

import gentoolkit.pprinter as pp
from gentoolkit import errors
from gentoolkit.equery import format_options, mod_usage
from gentoolkit.query import Query

# =======
# Globals
# =======

QUERY_OPTS = {
    "in_installed": True,
    "in_porttree": True,
    "in_overlay": True,
    "include_masked": True,
    "show_progress": False
}

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
    print(mod_usage(mod_name="dependencies"))
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

    matches = query.smart_find(**QUERY_OPTS)

    if not matches:
        raise errors.GentoolkitNoMatches(query)

    matches.sort()
    matches.reverse()
    
    pkgdeps = matches[0].deps
    deps = pkgdeps.get_all_depends(raw=True)

    print(' '.join(deps.split()))
    


if __name__ == '__main__':
    main(sys.argv)

