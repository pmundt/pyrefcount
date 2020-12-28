Examples
========

Producer/Consumer Example
-------------------------

As a simple example, we consider a class that uses a producer/consumer or publish/subscribe pattern, where we only wish
to launch the producer/publishing thread when consumers/subscribers have dynamically attached themselves to the class
instance. As this may happen at any time, a ``Refcounter`` is used for determining when to start and stop the thread:

.. code-block:: python

   import threading
   import time

   from refcount import Refcounter


   class StoppableThread(threading.Thread):
       def __init__(self):
           self._stopper = threading.Event()
           super().__init__()

       def stop(self):
           self._stopper.set()

       def run(self):
           while True:
               if self._stopper.isSet():
                   return
               print('iter from producer thread')
               time.sleep(1)


   class ProducerClass:
       def __init__(self):
           # Set the initial refcount to 0 instead of the default 1, the initial consumer
           # addition and producer thread launch is special-cased by add_consumer(). Special
           # care needs to be taken in this case, as any decrement operations will raise an
           # immediate underflow exception.
           self.consumers = Refcount(usecount=0)
           self.thread = None

       def add_consumer(self):
           print('Adding consumer, refcount before inc', self.consumers.refcount)
           if self.consumers.inc_not_zero() == False:
               # If the refcount is zero, manually increment it and launch the producer thread
               self.consumers.inc()

               print('Starting producer thread')
               self.thread = StoppableThread()
               self.thread.start()

       def del_consumer(self):
           print('Deleting consumer: refcount before dec', self.consumers.usecount)
           if self.consumers.dec_and_test():
               print('All consumers have exited, stopping producer thread')
               self.thread.stop()
               self.thread.join()

The two most straightforward scenarios to consider are:

- Adding/removing a single consumer
- Adding/removing multiple consumers

these are briefly exemplified below. To begin with, instantiate the ``ProducerClass()`` and add an initial consumer:

.. doctest::

   >>> producer = ProducerClass()
   >>> producer.add_consumer() # Add an initial consumer
   Adding consumer, refcount before inc 0
   Starting producer thread

we can now sleep for a couple of seconds and see the worker thread iterate:

.. doctest::

   >>> time.sleep(2)
   iter from producer thread
   iter from producer thread

Followed by removing the consumer and observing the thread shutdown:

.. doctest::

   >>> producer.del_consumer()
   Deleting consumer, refcount before dec 1
   All consumers have exited, stopping producer thread

The multi-consumer case is identical, with the refcount reflecting the active number of consumers, and the thread
shutdown not being triggered until all have exited:

.. doctest::

   >>> producer.add_consumer()
   Adding consumer, refcount before inc 0
   Starting producer thread
   >>> producer.add_consumer()
   Adding consumer, refcount before inc 1
   # do some work
   >>> producer.del_consumer()
   Deleting consumer, refcount before dec 2
   >>> producer.del_consumer()
   Deleting consumer, refcount before dec 1
   All consumers have exited, stopping producer thread

.. note:: While this case has exemplified `on-demand` spawning and shutdown of a single worker thread in response to
          consumer add/remove events, more complex real-world cases can also use the ``usecount`` value as a basis for
          determining the number of worker threads to spawn, either directly, or as part of a thread pool.

Instance Manager Example
------------------------

When using an `instance manager pattern <https://wiki.c2.com/?InstanceManagerPattern>`_, the manager may wish to modify
its behaviour dependent upon specific attributes set in instances under management. As the behaviour may be
computationally expensive (e.g. the conversion of large pandas DataFrames to cuDF ones), it is advantageous to be able
to avoid it entirely when there are no managed instances that depend on it.

An example of an ``InstanceManager`` class and managed subclasses that expect different data types to be handed down is
provided below (note that type conversion is only carried out when subclasses that require it are being managed):

.. code-block:: python

   from refcount import Refcounter
   from abc import ABC, abstractmethod


   class ParentClass(ABC):
       def __init__(self):
           pass

      @abstractmethod
      def execute(data):
           pass


   class NormalType:
       def __init__(self, value):
           self.value = value


   class ExpensiveType:
       def __init__(self, value):
           self.value = value

       @staticmethod
       def from_normal(normal):
           return ExpensiveType(normal.value)


   class NormalSubclass(ParentClass):
       def __init__(self):
           super().__init__()

       def execute(self, data):
           # Do something with NormalType data
           assert isinstance(data, NormalType)


   class ExpensiveSubclass(ParentClass):
       def __init__(self):
           # Set an attribute that will trigger type conversion in the instance manager
           self.example_attr = True
           super().__init__()

       def execute(self, data):
           # Do something with ExpensiveType data
           assert isinstance(data, ExpensiveType)


   class InstanceManager:
       def __init__(self, instances):
           # Do not carry out type conversion by default
           self.convert_data = False

           # Initialize refcount with 0 users. The first inc() will trigger the
           # acquire callback and set the convert_data flag.
           self.converted_data_users = Refcounter(usecount=0,
                                                  acquire=self.set_convert_data,
                                                  release=self.clear_convert_data)
           self.instances = []

           for instance in instances:
               self.add_instance(instance)

       def do_something(self):
           data = NormalType(value=True)

           if self.convert_data:
               print('Manager performing type conversion')

               # Carry out data type conversion for the instances that need it
               expensive_data = ExpensiveType.from_normal(data)
           else:
               print('Manager not performing type conversion')

           for instance in self.instances:
               if hasattr(instance, 'example_attr'):
                   instance.execute(expensive_data)
               else:
                   instance.execute(data)

       def set_convert_data(self):
           self.convert_data = True

       def clear_convert_data(self):
           self.convert_data = False

       def add_instance(self, instance):
           # Check for data conversion attribute in subclass instances
           if hasattr(instance, 'example_attr'):
               self.convert_data_users.inc()

           self.instances.append(instance)

       def remove_instance(self, instance):
           for i in self.instances:
               if i == instance:
                   if hasattr(instance, 'example_attr'):
                       self.convert_data_users.dec()
                   self.instances.remove(instance)
                   return

To see this in practice, we first instantiate the ``InstanceManager`` with a couple of ``NormalSubclass`` instances:

.. doctest::

    >>> manager = InstanceManager(instances=[NormalSubclass(), NormalSubclass()])
    >>> manager.do_something()
    Manager not performing type conversion

Next, add a couple of ``ExpensiveSubclass`` instances:

.. doctest::

   >>> expensive = ExpensiveSubclass()
   >>> manager.add_instance(expensive)
   >>> expensive2 = ExpensiveSubClass()
   >>> manager.add_instance(expensive2)
   >>> manager.do_something()
   Manager performing type conversion
   >>> manager.convert_data_users.usecount
   2

internally this sets up the ``convert_data_users`` attr as a refcount object, while the ``hasattr`` check in the
``add_instance()`` method increments the use count for each ``ExpensiveSubclass`` instance. The reference count
matches the number of added instances satisfying the attribute check. Now remove one instance:

.. doctest::

   >>> manager.remove_instance(expensive)
   >>> manager.do_something()
   Manager performing type conversion
   >>> manager.convert_data_users.usecount
   1

the instance is removed and the refcount is decremented, but the behaviour remains unchanged as there is still
a remaining user. The last user can now be removed:

.. doctest::

   >>> manager.remove_instance(expensive2)
   >>> manager.do_something()
   Manager not performing type conversion

the reference count is dropped to 0, causing the ``convert_data`` flag to be cleared by the release callback. Normal
operating behaviour is resumed. As expected, re-adding an ``ExpensiveSubclass`` instance triggers the behaviour
modification again:

.. doctest::

   >>> manager.add_instance(ExpensiveSubclass())
   >>> manager.do_something()
   Manager performing type conversion

.. note:: None of the assertions were triggered during the execution flow, indicating that each managed instance
          received the data type in the format it requires.