"""

    :mod:`refcount`
    ===============

    A simple library for providing a reference counter with optional acquire/release callbacks as well as access
    protection to reference counted values.

    .. moduleauthor:: Paul Mundt <paul.mundt@adaptant.io>
"""


# pylint: disable=unnecessary-pass
class UnderflowException(Exception):
    """
    Reference counter underflow exception, raised on counter underflow.

    >>> from refcount import Refcounter
    >>> ref = Refcounter()
    >>> ref.dec()
    >>> ref.usecount
    0
    >>> ref.dec() # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    refcount.UnderflowException: refcount underflow
    """
    pass


class Refcounter:
    """
    Provides a reference counter with an optional release callback that is triggered
    when the last user drops off.
    """
    def __init__(self, usecount=1, acquire=None, release=None):
        """
        Initialize a reference counter

        :param usecount: Initial refcount value
        :type usecount: int
        :param acquire: A callback function that is called when a reference count goes above 0
        :type acquire: function, optional
        :param release: A callback function that is called when the reference count drops to 0
        :type release: function, optional
        """
        self._usecount = usecount
        self._acquire = acquire
        self._release = release

    def add(self, value):
        """
        Add to a reference count

        If the reference count becomes higher than 0, the acquire callback (if provided) will be automatically
        triggered.

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> ref.add(2)
        >>> ref.usecount
        3

        :param value: Amount to add
        :type value: int
        """
        if self._usecount == 0 and self._acquire:
            self._usecount += value
            self._acquire()
        else:
            self._usecount += value

    def add_not_zero(self, value):
        """
        Add to a reference count unless it is 0

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> ref.dec()
        >>> ref.usecount
        0
        >>> ref.add_not_zero(2)
        False

        :param value: Amount to add
        :type value: int
        :return: False if refcount is 0, True otherwise
        """
        if self._usecount == 0:
            return False

        self.add(value)
        return True

    def inc(self):
        """
        Increment reference count by 1

        If the reference count becomes higher than 0, the acquire callback (if provided) will be automatically
        triggered.

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> ref.usecount
        1
        >>> ref.inc()
        >>> ref.usecount
        2
        """
        self.add(1)

    def inc_not_zero(self):
        """
        Increment a reference by 1 unless it is 0

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> ref.dec()
        >>> ref.usecount
        0
        >>> ref.inc_not_zero()
        False

        :return: False if refcount is 0, True otherwise
        """
        if self._usecount == 0:
            return False

        self.inc()
        return True

    def sub(self, value):
        """
        Subtract from a reference count

        >>> from refcount import Refcounter
        >>> ref = Refcounter(usecount=3)
        >>> ref.usecount
        3
        >>> ref.sub(2)
        >>> ref.usecount
        1

        If the reference count drops to 0, the release callback (if provided) will be automatically triggered.

        :param value: Amount to subtract
        :type value: int
        :raises UnderflowException: refcount underflow
        """
        if self._usecount - value < 0:
            raise UnderflowException('refcount underflow')

        self._usecount -= value

        if self._usecount == 0 and self._release is not None:
            self._release()

    def sub_and_test(self, value):
        """
        Subtract reference count and test if the reference count is 0

        This can be used by code that wishes to implement a cleanup path triggered only when the reference
        count drops to 0.

        If the reference count drops to 0, the release callback (if provided) will be automatically triggered.

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> ref.inc()
        >>> if ref.sub_and_test(2):
        ...     print('reference count is now 0')
        reference count is now 0

        :param value: Amount to subtract
        :type value: int
        :return: True if reference count is 0, otherwise False
        :rtype: bool
        :raises UnderflowException: refcount underflow
        """
        self.sub(value)
        return self._usecount == 0

    def dec(self):
        """
        Decrement reference count by 1

        If the reference count drops to 0, the release callback (if provided) will be automatically triggered.

        >>> from refcount import Refcounter
        >>> def refcount_released():
        ...     print('no more users')
        >>> ref = Refcounter(release=refcount_released)
        >>> ref.inc()
        >>> ref.dec()
        >>> ref.dec()
        no more users

        :raises UnderflowException: refcount underflow
        """
        self.sub(1)

    def dec_and_test(self):
        """
        Decrement reference count and test if the reference count is 0

        This can be used by code that wishes to implement a cleanup path triggered only when the reference
        count drops to 0.

        If the reference count drops to 0, the release callback (if provided) will be automatically triggered.

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> if ref.dec_and_test():
        ...     print('reference count is now 0')
        reference count is now 0

        :return: True if reference count is 0, otherwise False
        :rtype: bool
        :raises UnderflowException: refcount underflow
        """
        self.dec()
        return self._usecount == 0

    @property
    def usecount(self):
        """
        Read/write the reference count

        >>> from refcount import Refcounter
        >>> ref = Refcounter()
        >>> ref.usecount
        1
        >>> ref.inc()
        >>> ref.usecount
        2
        >>> ref.usecount = 4
        >>> ref.usecount
        4

        :return: Current reference count
        :rtype: int
        """
        return self._usecount

    @usecount.setter
    def usecount(self, value):
        self._usecount = value


class RefcountedValue(Refcounter):
    """
    Provides access protection to a reference counted value.

    Allows the reference counting for a value to be arbitrarily incremented and decremented, permitting access to
    the protected value so long as a valid reference count is held. Once the reference count has dropped to 0,
    continued references will raise a NameError exception. A release callback method may optionally be provided,
    and will be called as soon as the last remaining reference is dropped.
    """
    def __init__(self, value, usecount=1, acquire=None, release=None):
        """
        Initialize a reference counted value

        :param value: The protected reference counted value
        :type value: Any
        :param usecount: Initial refcount value
        :type usecount: int
        :param acquire: A callback function that is called when a reference count goes above 0
        :type acquire: function, optional
        :param release: A callback function that is called when the reference count drops to 0
        :type release: function, optional
        """
        self._value = value

        super().__init__(usecount=usecount, acquire=acquire, release=release)

    @property
    def value(self):
        """
        Reference count protected value

        Allows access to the protected value as long as a valid reference count is held.

        >>> from refcount import RefcountedValue
        >>> ref = RefcountedValue(value=True)
        >>> ref.value
        True
        >>> ref.dec()
        >>> ref.value # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        NameError: Value referenced with no reference count

        :return: value
        :raises NameError: Value referenced with no reference count
        """
        if self._usecount == 0:
            raise NameError('Value referenced with no reference count')
        return self._value

    @value.setter
    def value(self, value):
        if self._usecount == 0:
            raise NameError('Value referenced with no reference count')
        self._value = value
