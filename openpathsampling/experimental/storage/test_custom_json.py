from .custom_json import *
import json
import pytest

import numpy as np
from numpy import testing as npt
from simtk import unit

from . import test_serialization_helpers

class CustomJSONCodingTest(object):
    def test_default(self):
        for (obj, dct) in zip(self.objs, self.dcts):
            assert self.codec.default(obj) == dct

    def test_object_hook(self):
        for (obj, dct) in zip(self.objs, self.dcts):
            assert self.codec.object_hook(dct) == obj

    def test_round_trip(self):
        encoder, decoder = custom_json_factory([self.codec])
        for (obj, dct) in zip(self.objs, self.dcts):
            json_str = json.dumps(obj, cls=encoder)
            reconstructed = json.loads(json_str, cls=decoder)
            assert reconstructed == obj
            json_str_2 = json.dumps(obj, cls=encoder)
            assert json_str == json_str_2

class TestNumpyCoding(CustomJSONCodingTest):
    def setup(self):
        self.codec = numpy_codec
        self.objs = [np.array([[1.0, 0.0], [2.0, 3.2]]),
                     np.array([1, 0])]
        shapes = [(2, 2), (2,)]
        dtypes = [str(arr.dtype) for arr in self.objs]  # may change by system?
        string_reps = [arr.tobytes() for arr in self.objs]
        self.dcts = [
            {
                '__class__': 'ndarray',
                '__module__': 'numpy',
                 'shape': shape,
                 'dtype': dtype,
                 'string': string_rep
            }
            for shape, dtype, string_rep in zip(shapes, dtypes, string_reps)
        ]

    def test_object_hook(self):
        # to get custom equality testing for numpy
        for (obj, dct) in zip(self.objs, self.dcts):
            reconstructed = self.codec.object_hook(dct)
            npt.assert_array_equal(reconstructed, obj)

    def test_round_trip(self):
        encoder, decoder = custom_json_factory([self.codec, bytes_codec])
        for (obj, dct) in zip(self.objs, self.dcts):
            json_str = json.dumps(obj, cls=encoder)
            reconstructed = json.loads(json_str, cls=decoder)
            npt.assert_array_equal(reconstructed, obj)
            json_str_2 = json.dumps(obj, cls=encoder)
            assert json_str == json_str_2

class TestUUIDCoding(object):
    def setup(self):
        self.codec = uuid_object_codec
        all_objs = test_serialization_helpers.all_objects
        self.objs = [all_objs['int'], all_objs['str']]
        updates = [{'normal_attr': 5, 'name': 'int'},
                   {'normal_attr': 'foo', 'name': 'str'}]
        module = str(test_serialization_helpers)
        self.dcts = [
            {
                '__class__': 'MockUUIDObject',
                '__module__': test_serialization_helpers.__name__,
                'normal_attr': None,
                'obj_attr': None,
                'list_attr': None,
                'dict_attr': None,
                'lazy_attr': None,
            }
            for _ in self.objs
        ]
        for dct, update in zip(self.dcts, updates):
            dct.update(update)

    test_default = CustomJSONCodingTest.test_default

    def test_object_hook(self):
        for (obj, dct) in zip(self.objs, self.dcts):
            assert self.codec.object_hook(dct) == dct


