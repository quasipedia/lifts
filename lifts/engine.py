#! /usr/bin/env python3
import asyncio
import weakref
from collections import defaultdict


class EntityRegistry:

    __instances = defaultdict(set)

    @classmethod
    def add(cls, instance):
        cls.__instances[instance.__class__].add(weakref.ref(instance))

    @classmethod
    def remove(cls, instance):
        for ref in weakref.getweakrefs(instance):
            cls.__instances[instance.__class__].discard(ref)

    @classmethod
    def instances(cls, class_):
        references = [i() for i in cls.__instances[class_]]
        yield from filter(lambda r: r is not None, references)

    @classmethod
    def classes(cls):
        yield from (k for k in cls.__instances)

    @classmethod
    def reset(cls):
        cls.__instances = defaultdict(set)


class SimObject:

    '''An abstract class for any object in the simulation.'''

    __refs__ = defaultdict(list)

    def __init__(self):
        self.listening_entities = set()
        EntityRegistry.add(self)

    @asyncio.coroutine
    def perform_step(self):
        yield from self.step()

    def listen(self, entity):
        '''Listen to the events emitted by an entity.'''
        if not isinstance(entity, SimObject):
            msg = 'Only possible to listen to "SimObject", not "{}"'
            raise ValueError(msg.format(entity.__class__.__name__))
        entity.listening_entities.add(self)

    def forget(self, entity):
        '''Ignore messages coming from an entity.'''
        entity.listening_entities.discard(self)

    def emit(self, payload):
        '''Send a message to all listening entities.'''
        for entity in self.listening_entities:
            entity.process(payload)


class Simulation:

    '''The main simulation object.'''

    def run(self, classes=None):
        self.__loop = asyncio.get_event_loop()
        self.__tasks = []
        classes = classes or EntityRegistry.classes()
        for class_ in classes:
            for instance in EntityRegistry.instances(class_):
                self.__tasks.append(asyncio.async(instance.perform_step()))
        self.__loop.run_until_complete(asyncio.wait([future]))
