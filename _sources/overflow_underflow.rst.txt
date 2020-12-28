refcount Overflow/Underflow
---------------------------

A common concern for reference counters is handling overflow and underflow cases. The way these are handled by the
``refcount`` package are described in more detail below.

refcount Overflow
*****************

Counter overflow within ``refcount`` is avoided by nature of python's type system. While the counter is initialized as
an integer type, integers in python (at least since python 3) are implemented with
`arbitrary-precision <https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic>`_, and require no specific
awareness or handling by the user.

refcount Underflow
******************

The more common case is that of counter underflow, which will be triggered any time a reference counter is decremented
below 0. This case is handled by :py:exc:`refcount.UnderflowException`, which will be raised for any operations that
would cause the counter to underflow.
