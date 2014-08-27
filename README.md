`hippools` is a simple service for Internet Protocol address management (IPAM), written in Python.

- IPv4 management (IPv6 in our plans)
- RESTFul-like API
- Python API client

Based on :
- netaddr https://pypi.python.org/pypi/netaddr
- Flask-RESTful http://flask-restful.readthedocs.org/en/latest/

[![Build Status](https://travis-ci.org/hayorov/hippools.svg?branch=master)](https://travis-ci.org/hayorov/hippools)

-------
Changes
-------
12/04/2013 Hello world

-------
License
-------

This software is released under Apache License

See http://www.apache.org/licenses/LICENSE-2.0.html for full text.

------------
Dependencies
------------

Python 2.6 or higher.
More info in requirements.txt

-------------
Documentation
-------------

The code contains thorough docstrings as well as detailed tutorials and
API documentation can be found here:

http://foo/

-------------
How to run
-------------
gunicorn -b 0.0.0.0:5001 hippools.app:app

--------------
And finally...
--------------

Share and enjoy!
