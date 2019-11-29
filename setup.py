#!/usr/bin/env python
#
# Copyright (c) 2002-2009 Gentoo Foundation
# Copyright (c) 2019, MAD Hacking
#
# Distributed under the terms of the GNU General Public License v2 or later

from __future__ import print_function

import re
import sys
import subprocess
from distutils import core
from distutils.cmd import Command
from glob import glob

import os
import io

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pym'))

if ( len(sys.argv) > 2 ) and ( sys.argv[1] == "set_version" ):
	__version__ = sys.argv[2]
else:
	__version__ = os.getenv('VERSION', default=os.getenv('PVR', default='9999'))

cwd = os.getcwd()

# Load EPREFIX from Portage, fall back to the empty string if it fails
try:
	from portage.const import EPREFIX
except ImportError:
	EPREFIX=''


# Bash files that need `VERSION=""` subbed, relative to this dir:
bash_scripts = [(os.path.join(cwd, path), 'VERSION=') for path in (
)]

# Python files that need `__version__ = ""` subbed, relative to this dir:
python_scripts = [(os.path.join(cwd, path), '__version__ = ') for path in (
	'pym/gentoolkit/kwtool/__init__.py'
)]

manpages = [(os.path.join(cwd, path[0]), path[1]) for path in (
)]

class set_version(core.Command):
	"""Set python __version__ and bash VERSION to our __version__."""
	description = "hardcode scripts' version using VERSION from environment"
	user_options = []  # [(long_name, short_name, desc),]

	def initialize_options (self):
		pass

	def finalize_options (self):
		pass

	def run(self):
		ver = 'git' if __version__ == '9999' else __version__
		print("Setting version to %s" % ver)
		def sub(files, pattern):
			for f in files:
				updated_file = []
				with io.open(f[0], 'r', 1, 'utf_8') as s:
					for line in s:
						newline = re.sub(pattern %f[1], '"%s"' % ver, line, 1)
						updated_file.append(newline)
				with io.open(f[0], 'w', 1, 'utf_8') as s:
					s.writelines(updated_file)

		quote = r'[\'"]{1}'
		bash_re = r'(?<=%s)' + quote + '[^\'"]*' + quote
		sub(bash_scripts, bash_re)
		python_re = r'(?<=^%s)' + quote + '[^\'"]*' + quote
		sub(python_scripts, python_re)
		man_re = r'(?<=^.TH "%s" "[0-9]" )' + quote + '[^\'"]*' + quote
		sub(manpages, man_re)


class TestCommand(Command):
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		args = [sys.executable, '-m', 'unittest', 'discover', 'pym']
		raise SystemExit(subprocess.call(args))


packages = [
	str('.'.join(root.split(os.sep)[1:]))
	for root, dirs, files in os.walk('pym/gentoolkit')
	if '__init__.py' in files
]

test_data = {
	'gentoolbox': [
	]
}

core.setup(
	name='gentoolbox',
	version=__version__,
	description='Set of tools that work with and enhance portage.',
	author='Max Hacking',
	author_email='gentoolbox@mad-hacking.net',
	maintainer='Max Hacking',
	maintainer_email='gentoolbox@mad-hacking.net',
	url='https://github.com/hacking-gentoo/gentoolbox',
	download_url='https://github.com/hacking-gentoo/gentoolbox/archive/%s.tar.gz'\
		% __version__,
	package_dir={'': 'pym'},
	packages=packages,
	package_data = test_data,
	scripts=(glob('bin/*')),
	data_files=(
	),
	cmdclass={
		'test': TestCommand,
		'set_version': set_version,
	},
)

# vim: set ts=4 sw=4 tw=79:
