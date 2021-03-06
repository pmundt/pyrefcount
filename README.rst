pyrefcount
==========

|build| |license| |python-version| |pypi-version|

.. |build| image:: https://img.shields.io/github/workflow/status/pmundt/pyrefcount/Python%20package
   :alt: GitHub Workflow Status
   :target: https://github.com/pmundt/pyrefcount/actions

.. |license| image:: https://img.shields.io/pypi/l/pyrefcount
   :alt: MIT License

.. |python-version| image:: https://img.shields.io/pypi/pyversions/pyrefcount
   :alt: PyPI - Python Version
   :target: https://pypi.python.org/pypi/pyrefcount

.. |pypi-version| image:: https://img.shields.io/pypi/v/pyrefcount
   :alt: PyPI
   :target: https://pypi.python.org/pypi/pyrefcount

``pyrefcount`` provides a simple API for reference counting, providing protected access to reference counted values,
and for allowing acquire/release actions to be carried out when a reference count becomes active, or the last user
drops off, respectively. ``pyrefcount`` is inspired by the Linux Kernel's `refcount_t`_ API.

Usage
-----

Usage of pyrefcount is straightforward:

>>> from refcount import Refcounter
>>> ref = Refcounter()
>>> ref.inc()
>>> ref.usecount
2
>>> ref.dec()
>>> if ref.dec_and_test():
...     print('refcount is now 0, do something here')

For more complex usage examples and a complete API reference, refer to the `package documentation`_.

Features and Bugs
-----------------

Please file feature requests and bug reports in the `issue tracker`_.

License
-------

``pyrefcount`` is licensed under the MIT license.

.. _package documentation: https://pmundt.github.io/pyrefcount
.. _refcount_t: https://github.com/torvalds/linux/blob/master/include/linux/refcount.h
.. _issue tracker: https://github.com/pmundt/pyrefcount/issues
