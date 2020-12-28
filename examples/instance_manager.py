from abc import ABC, abstractmethod
from refcount import Refcounter


class ParentClass(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, data):
        pass


class ExpensiveType:
    def __init__(self, value):
        self.value = value

    @staticmethod
    def from_normal(normal):
        return ExpensiveType(normal.value)


class NormalType:
    def __init__(self, value):
        self.value = value


class ExpensiveSubclass(ParentClass):
    def __init__(self):
        self.example_attr = True
        super().__init__()

    def execute(self, data):
        assert isinstance(data, ExpensiveType)
        # Do something with ExpensiveType data
        print('------', type(data).__name__)


class NormalSubclass(ParentClass):
    def execute(self, data):
        assert isinstance(data, NormalType)
        # Do something with NormalType data
        print('------', type(data).__name__)


class InstanceManager:
    def __init__(self, instances):
        # Do not carry out type conversion by default
        self.convert_data = False

        # Initialize refcount with 0 users. The first inc() will trigger
        # the acquire callback.
        self.converted_data_users = Refcounter(usecount=0,
                                               acquire=self.set_convert_data,
                                               release=self.clear_convert_data)
        self.instances = []

        for instance in instances:
            self.add_instance(instance)

    def do_something(self):
        data = NormalType(value=True)

        if self.convert_data:
            converted_data = ExpensiveType.from_normal(data)
            print('-- Manager performing type conversion')
        else:
            print('-- Manager not performing type conversion')

        for instance in self.instances:
            print('---- Executing', type(instance).__name__)
            if hasattr(instance, 'example_attr'):
                instance.execute(converted_data)
            else:
                instance.execute(data)

    def set_convert_data(self):
        self.convert_data = True

    def clear_convert_data(self):
        self.convert_data = False

    def add_instance(self, instance):
        if hasattr(instance, 'example_attr'):
            self.converted_data_users.inc()

        self.instances.append(instance)

    def remove_instance(self, instance):
        for i in self.instances:
            if i == instance:
                if hasattr(instance, 'example_attr'):
                    self.converted_data_users.dec()
                self.instances.remove(instance)
                return


def main():
    print('Initiate the manager with a couple of normal subclasses')
    manager = InstanceManager(instances=[NormalSubclass(), NormalSubclass()])
    manager.do_something() # Normal

    print('\nAdding a couple of expensive subclass instances')
    expensive = ExpensiveSubclass()
    manager.add_instance(expensive)

    expensive2 = ExpensiveSubclass()
    manager.add_instance(expensive2)

    manager.do_something() # Expensive - refcount is 2

    print('\nRemoving one expensive instance')
    manager.remove_instance(expensive) # refcount is now 1
    manager.do_something() # Expensive

    print('\nRemove another expensive instance')
    manager.remove_instance(expensive2) # refcount is now 0, convert_data flag cleared
    manager.do_something() # Normal

    print('\nRe-adding an expensive instance')
    manager.add_instance(ExpensiveSubclass())
    manager.do_something() # Expensive


if __name__ == '__main__':
    main()
