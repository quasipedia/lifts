'''Test suite for the engine module.'''

import unittest
import unittest.mock as mock

from lifts.engine import EntityRegistry, SimObject, Simulation


class Dumb:

    pass


class Entity(SimObject):

    '''A SimObject generated for testing purposes'''

    def __init__(self):
        super().__init__()
        self.processor = mock.MagicMock()

    def step(self):
        counter = 0
        while counter < 3:
            counter += 1
            yield counter

    def process(self, payload):
        self.processor(payload)


class TestEntityRegistry(unittest.TestCase):

    '''Test suite for the EntityRegistry class'''

    def setUp(self):
        self.foo = Dumb()
        EntityRegistry.add(self.foo)
        self.instances = lambda: list(EntityRegistry.instances(Dumb))

    def tearDown(self):
        EntityRegistry.reset()

    def test_add(self):
        '''It is possible to add an instance to the registry.'''
        self.assertEqual([self.foo], self.instances())

    def test_remove(self):
        '''It is possible to remove an instance from the registry.'''
        EntityRegistry.remove(self.foo)
        self.assertEqual([], self.instances())

    def test_classes(self):
        '''It is possible to see what SimObject subclasses are instantiated.'''
        self.assertEqual([Dumb], list(EntityRegistry.classes()))

    def test_reset(self):
        '''It is possible to reset the registry.'''
        EntityRegistry.reset()
        self.assertEqual([], list(EntityRegistry.classes()))


class TestSimObject(unittest.TestCase):

    '''Test suite for the SimObject class'''

    def setUp(self):
        self.one = Entity()
        self.two = Entity()
        self.two.listen(self.one)
        self.payload = {'foo': 'bar'}

    def tearDown(self):
        EntityRegistry.reset()

    def test_auto_added(self):
        '''A new entity is automagically added to the registry.'''
        self.assertEqual(set((self.one, self.two)),
                         set(EntityRegistry.instances(Entity)))

    def test_listen_and_emit(self):
        '''Binding of message listening works.'''
        self.one.emit(self.payload)
        self.two.processor.assert_called_once_with(self.payload)

    def test_list_to_simobjects_only(self):
        '''Only SimObjects children can be listened to.'''
        self.assertRaises(ValueError, self.one.listen, Dumb())

    def test_forget(self):
        '''Unbinding of message listening works.'''
        self.two.forget(self.one)
        self.one.emit(self.payload)
        self.assertFalse(self.two.processor.called)

    def test_perform_step(self):
        '''Coroutine mechanism for steps works.'''
        expected = [1, 2, 3]
        actual = list(self.one.perform_step())
        self.assertEqual(expected, actual)


class TestSimulation(unittest.TestCase):

    '''Test suite for the SimObject class'''
