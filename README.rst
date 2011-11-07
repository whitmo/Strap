========
 'Strap
========

A utility library and script for building self contained bootstraps.


What / Why
==========

Strap provides a simple way to create a simple style installer for one
or more python packages that does not require network access or any
dependency other than python itself.

Some problems 'Strap addresses::

 * Installation of software with bad or intermittent network access.

 * Insuring a know good working set of packages

 * Simply setting up a virtualenv with all necessary software
   installed.


The ergonomics of use are similar to Java war and jar files with a
couple important differences.  First, a strap creates a sandbox for
code execution (a virtualenv).  Second, all code is installed via pip
vs. run from precompiled byte code.





