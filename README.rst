KismetDice
==========

A ZNC module, written in Python to provide dice for the Kismet Roleplaying Game System

To install, copy the entire package (dice/) into the ZNC module directory.

setup.py?
---------

There is no setup.py for this package.  The reasons are numerous, but it comes
down to there being no sane way to trick Setuptools to install a package into
an arbitrary directory; Distutils and Setuptools (the two main libraries used
for creating setup scripts) are designed to put module into site-packages, and
have a lot of meta-data cruft around that.  That is not something we can use in
a ZNC module.
