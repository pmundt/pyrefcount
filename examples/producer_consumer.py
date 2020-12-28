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
            print('-- iter from producer thread')
            time.sleep(1)


class ProducerClass:
    def __init__(self):
        # Set the initial refcount to 0 instead of the default 1, the initial consumer
        # addition and producer thread launch is special-cased by add_consumer(). Special
        # care needs to be taken in this case, as any decrement operations will raise an
        # immediate underflow exception.
        self.consumers = Refcounter(usecount=0)
        self.thread = None

    def add_consumer(self):
        print('Adding consumer, refcount before inc', self.consumers.usecount)
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


if __name__ == '__main__':
    producer = ProducerClass()

    print('*** Add and remove a single consumer from a producer ***')
    producer.add_consumer()
    time.sleep(5)
    producer.del_consumer()

    print('\n*** Add and remove multiple consumers from a producer ***')
    producer.add_consumer()
    time.sleep(3)
    producer.add_consumer()
    time.sleep(3)
    producer.del_consumer()
    time.sleep(3)
    producer.del_consumer()
