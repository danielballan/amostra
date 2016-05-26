from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import time as ttime
import pytest
import uuid
from amostra.testing import amostra_local_setup, amostra_local_teardown
from amostra.client.local_commands import (LocalSampleReference,
                                           LocalContainerReference,
                                           LocalRequestReference)


def setup():
    amostra_local_setup()

def test_constructors():
    # attempt empty reference create
    s_ref = LocalSampleReference()
    c_ref = LocalContainerReference()
    r_ref = LocalRequestReference()

def test_create_sample():
    s = LocalSampleReference()
    s.create(uid=str(uuid.uuid4()), name='local roman',
             time=ttime.time(), compound='Fe', material='sword')


def test_create_request():
    r = LocalRequestReference()
    r.create(sample=None, time=ttime.time(), uid=str(uuid.uuid4()))


def test_create_container():
    c = LocalContainerReference()
    c.create(time=ttime.time(), uid=str(uuid.uuid4()), name='village',
             type='ancient gaul')


def test_find_sample():
    s = LocalSampleReference()
    samp_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='hidefix',
                     kind='dog', breed='multigree')
    s.create(**samp_dict)
    assert next(s.find(uid=samp_dict['uid']))['uid'] == samp_dict['uid']


def test_find_container():
    c = LocalContainerReference()
    cont_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='village',
                     kind='gaul', population='50')
    c.create(**cont_dict)
    assert next(c.find(uid=cont_dict['uid']))['uid'] == cont_dict['uid']


def test_find_request():
    r = LocalRequestReference()
    req_dict = dict(uid=str(uuid.uuid4()), time=ttime.time(), name='war',
                     kind='street fight', state='inactive', winner='gauls')
    r.create(**req_dict)
    assert next(r.find(uid=req_dict['uid']))['uid'] == req_dict['uid']




def teardown():
    amostra_local_teardown()
