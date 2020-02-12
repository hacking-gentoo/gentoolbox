# Copyright(c) 2009, Gentoo Foundation
# Copyright(c) 2019, MAD Hacking
#
# Licensed under the GNU General Public License, v2

"""Display the best keywords for a given package"""

from __future__ import print_function

# =======
# Imports
# =======

import sys
from getopt import gnu_getopt, GetoptError

from portage.dep import paren_reduce

import gentoolkit.pprinter as pp
from gentoolkit import errors
from gentoolkit.equery import format_options, mod_usage, CONFIG
from gentoolkit.atom import Atom
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
    print(mod_usage(mod_name="dependencies"))
    print()
    print(pp.command("options"))
    print(format_options((
        (" -h, --help", "display this help message"),
    )))


def parse_module_options(module_opts):
    """Parse module options"""

    opts = (x[0] for x in module_opts)
    for opt in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(0)


def best_keyword(kw1, kw2):
    # If kw1 is not masked in any way then it is already the best it can get.
    if kw1[0] != '-' and kw1[0] != '~':
        return kw1
    # If kw1 is hard masked and kw2 is anything else then kw2 is best.
    if kw1[0] == '-' and kw2[0] != '-':
        return kw2
    # If kw1 is soft masked and kw1 is not masked at all then kw2 is best.
    if kw1[0] == '~' and (kw2[0] != '-' and kw2[0] != '~'):
        return kw2
    # Assume kw1 is already as good as we're getting.
    return kw1


def worst_keyword(kw1, kw2):
    # If kw1 is hard masked then it is already as bad as it can get
    if kw1[0] == '-':
        return kw1
    # If kw1 is masked and kw2 is not then kw1 is worst.
    if kw1[0] == '~' and (kw2[0] != '~' and kw2[0] != '-'):
        return kw1
    # If kw1 is not hard or soft masked then whatever kw2 is it can't be better
    return kw2


def make_stable(arch):
    return arch[1:] if (arch[0] == '~' or arch[0] == '-') else arch


def combibe_kwdicts(kwdict, pkwdict, combine=False):
    if combine:
        # Loop through all the arch keywords for this package. If they are not in the combined
        # keywords then add this one. If they are already in the combined keywords then replace
        # it with this one if it is better.
        for (k, v) in pkwdict.items():
            if kwdict.get(k) == None:
                kwdict[k] = v
            else:
                kwdict[k] = best_keyword(kwdict[k], v)
    else:
        # Loop through all combined keywords. If this package has no corresponding keyword then
        # remove it from the combined list. If it does have a corresponding keyword then replace
        # the combined keyword with whichever is worst. We have to defer deleting the dictionary
        # entry as you can't delete from a dictionary whilst iterating on it.
        tbd = []
        for (k, v) in kwdict.items():
            if pkwdict.get(k) == None:
                tbd.append(k)
            else:
                kwdict[k] = worst_keyword(pkwdict[k], v)
        for k in tbd:
            if kwdict.get(k) is not None:
                del kwdict[k]


def parse_atom(tok, indent=0):
    """Parse dependency atom"""

    assert(not isinstance(tok, list))
    
    if CONFIG['verbose']:
        print(' ' * indent, 'atom', tok)

    atom = Atom(tok)

    # Try to find matches for this atom
    query = Query(atom)
    matches = query.find(include_masked=True)
    # We didn't find any so raise an error
    if not matches:
        raise errors.GentoolkitNoMatches(query)
    
    # Loop through the matching packages combining their best arch keywords into a single dictionary
    matches.sort()
    kwdict = {}
    for pkg in matches:
        if CONFIG['verbose']:
            print(' ' * (indent + 2), pkg)
        keywords_str = pkg.environment(('KEYWORDS'), prefer_vdb=False)
        if keywords_str:
            if CONFIG['verbose']:
                print(' ' * (indent + 4), keywords_str)
            for keyword in keywords_str.split():
                skw = make_stable(keyword)
                if skw not in kwdict:
                    kwdict[skw] = keyword;
                else:
                    kwdict[skw] = best_keyword(kwdict[skw], keyword)
        
    if CONFIG['verbose']:
        print(' ' * indent, 'return', kwdict)

    return kwdict


def parse_list(tok, combine=False, indent=0):
    """Parse dependency list"""

    assert(isinstance(tok, list))

    if CONFIG['verbose']:
        print(' ' * indent, 'list', tok)
        
    indent += 2
    kwdict = None
    
    while len(tok) > 0:
        # Get the next token
        subtok = tok.pop(0)
        
        # If it is a blocker then ignore it
        if subtok[0] == '!':
            if CONFIG['verbose']:
                print(' ' * indent, 'block', tok)
        # If it is a use-flag then process it as a normal list
        elif subtok[-1] == '?':
            nextok = tok.pop(0)
            if CONFIG['verbose']:
                print(' ' * indent, 'use-flag', subtok, nextok)
            pkwdict = parse_list(nextok, False, indent + 2)
        # If it is a list of alternatives then process it as a combined list    
        elif subtok == '||':
            nextok = tok.pop(0)
            if CONFIG['verbose']:
                print(' ' * indent, subtok, nextok)
            pkwdict = parse_list(nextok, True, indent + 2)
        else:
            # It must be an atom so parse it for combined arch keywords
            pkwdict = parse_atom(subtok, indent)
        
        # If this is the first time round the loop then whatever keywords we have collected
        # thus far are good.         
        if kwdict is None:
            kwdict = pkwdict
            continue

        combibe_kwdicts(kwdict, pkwdict, combine)

    indent -= 2

    if CONFIG['verbose']:
        print(' ' * indent, 'return', kwdict)

    return kwdict


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
    
    pkgdeps = matches[0].deps
    deps = pkgdeps.get_all_depends(raw=True)
    deps = paren_reduce(deps)

    if CONFIG['verbose']:
        print(deps)
        print()
    
    kwdict = parse_list(deps)

    if CONFIG['verbose']:
        print()
        
    if not kwdict == None:
        print(' '.join(kwdict.values()))
    else:
        print()

    
if __name__ == '__main__':
    main(sys.argv)

