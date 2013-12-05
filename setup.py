#!/usr/bin/python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import setuptools
import hippools


def main():
    if sys.version_info[:2] < (2, 6):
        sys.stderr.write("hippools requires Python version 2.6 or higher.\n")
        sys.exit(1)

    if sys.argv[-1] == 'setup.py':
        sys.stdout.write("To install, run 'python setup.py install'\n\n")

    setuptools.setup(
        name="hippools",
        version=hippools.__version__,
        author='Alexander Hayorov',
        author_email='i@hayorov.ru',
        description="Simple IPAM service with RESTful-like API",
        long_description=read('README.md'),
        license='Apache',
        url='http://hayorov.ru/',
        packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
        include_package_data=True,
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Science/Research',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Telecommunications Industry',
            'License :: OSI Approved :: BSD License',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Topic :: Communications',
            'Topic :: Documentation',
            'Topic :: Education',
            'Topic :: Education :: Testing',
            'Topic :: Home Automation',
            'Topic :: Internet',
            'Topic :: Internet :: Log Analysis',
            'Topic :: Internet :: Name Service (DNS)',
            'Topic :: Internet :: Proxy Servers',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
            'Topic :: Internet :: WWW/HTTP :: Site Management',
            'Topic :: Security',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing',
            'Topic :: Software Development :: Testing :: Traffic Generation',
            'Topic :: System :: Benchmark',
            'Topic :: System :: Clustering',
            'Topic :: System :: Distributed Computing',
            'Topic :: System :: Installation/Setup',
            'Topic :: System :: Logging',
            'Topic :: System :: Monitoring',
            'Topic :: System :: Networking',
            'Topic :: System :: Networking :: Firewalls',
            'Topic :: System :: Networking :: Monitoring',
            'Topic :: System :: Networking :: Time Synchronization',
            'Topic :: System :: Recovery Tools',
            'Topic :: System :: Shells',
            'Topic :: System :: Software Distribution',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: System Shells',
            'Topic :: Text Processing',
            'Topic :: Text Processing :: Filters',
            'Topic :: Utilities',
        ],
        install_requires=read('requirements.txt').splitlines(),
    )


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if __name__ == "__main__":
    main()
