.. pyrefcount documentation master file, created by
   sphinx-quickstart on Fri Dec 25 02:09:05 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyrefcount's documentation!
======================================

The goal of ``refcount`` is to provide a simple API for reference counting, providing protected access to reference
counted values, and for allowing acquire/release actions to be carried out when a reference count becomes active, or
the last user drops off, respectively. ``refcount`` is inspired by the Linux Kernel's `refcount_t`_ API.

Motivation
----------

While python implements reference counting at the object level through ``sys.getrefcount(object)``, there was no
straightforward mechanism for allowing reference counts to be independently defined and controlled.

An example case that motivated this work was a situation where an instance manager class that instantiates
and manages multiple subclasses (extended from the same base class) sets a value that only a subset of managed
instances make use of, and which modifies the behaviour of the instance manager. These managed instances may be
arbitrarily created or deleted, and once the last dependent subclass instance has terminated, the manager wishes to
clear the behaviour-modifying value and return to its original behaviour. This particular case involved the
computationally expensive conversion of large pandas DataFrames to cuDF ones, which can be skipped when there are no
longer any dependent instances that explicitly require cuDF DataFrames to be passed down.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   overflow_underflow
   examples
   refcount

.. _refcount_t: https://github.com/torvalds/linux/blob/master/include/linux/refcount.h

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
