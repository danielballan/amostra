from doct import Document
import ujson
from uuid import uuid4
import requests
import time
from amostra.client import conf


class SampleReference:
    """Reference implementation of generic sample manager
    This is primarily a reference implementation / for testing but can be
    used in production for very small numbers of samples.

    """
    def __init__(self, sample_list=[], host=conf.conn_config['host'],
                 port=conf.conn_config['port']):
        """
        Parameters
        ----------
        sample_list:List of desired sample(s) to be created
        host
        port

        Returns
        -------

        """
        self._server_path = 'http://{}:{}/' .format(host, port)
        if sample_list is None:
            sample_list = []
        self._sample_list = [dict(d) for d in sample_list]
        ln = len(self._sample_list)
        if ln != len(set(d['name'] for d in self._sample_list)):
            raise ValueError("duplicate names")
        if ln != len(set(d['uid'] for d in self._sample_list)):
            raise ValueError("duplicate uids")
        if sample_list:
            # if there is a list in mind, create it
            domt = ujson.dumps(self._sample_list)
            r = requests.post(self._server_path + 'sample',
                              data=domt)
            r.raise_for_status()

    def add(self, name, time=time.time(), uid=str(uuid4()),
            **kwargs):
        """Add a sample to the database
        All kwargs are collected and passed through to the documents

        Parameters
        ----------
        name : str
            The name of the sample.  This must be unique in the database

        schema : str, optional
             The schema used to validate the kwargs prior to inserting
             into the database.  The schema must allow for 'uid',
             'schema', and 'name' string fields.

        Returns
        -------
        uid : str
            uid of the inserted document.
        """
        if any(d['name'] == name for d in self._sample_list):
            raise ValueError(
                "document with name {} already exists".format(name))
        doc = dict(uid=uid, name=name, time=time, 
                   **kwargs)
        domt = ujson.dumps(doc)
        r = requests.post(self._server_path + 'sample',
                          data=domt)
        r.raise_for_status()
        self._sample_list.append(doc)
        return ujson.loads(r.text)[0]

    def update(self, filter, update, host=conf.conn_config['host'], 
               port=conf.conn_config['port']):
        payload = dict(filter=filter, update=update)
        r = requests.put(url=self._server_path + 'sample',
                          data=ujson.dumps(payload))
        
    def find(self, **kwargs):
        """Find samples by keys
        First iterates over samples created by this instance,
        if sample not found, makes the trip to the server.
        Yields all documents which have all of the keys equal
        to the kwargs.  ex ::

            for k, v in kwargs:
                assert d[k] == v

        for all `d` yielded.

        No kwargs yields matches all samples.

        Yields
        ------
        c : dict
            Documents which have all keys with the given values

        """
        r = requests.get(self._server_path + 'sample',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._sample_list.extend(content)
        for c in content:
            yield Document('sample', c)

    def find_raw_mongo(self, mongo_query, json=False):
        """Return raw dicts or json instead of doct"""
        r = requests.get(self._server_path + '/sample',
                         params=ujson.dumps(mongo_query))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._sample_list.extend(content)
        for c in content:
            yield c

    def dump_to_json(self, fpath):
        # Seems done
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                ujson.dump(self._sample_list, fout)
        else:
            ujson.dump(self._sample_list, fpath)

    def dump_to_yaml(self, fpath):
        """For those who don't want to write into the database or work offline."""
        import yaml
        if isinstance(fpath, str):
            with open(fpath, 'w') as fout:
                yaml.dump(self._sample_list, fout)
        else:
            yaml.dump(self._sample_list, fpath)

    def get_schema(self):
        """Get information about schema from the server side"""
        r = requests.get(self._server_path +
                        '/schema_ref', params=ujson.dumps('sample'))
        r.raise_for_status()
        return ujson.loads(r.text)

    def get_requests(self):
        """Get all active requests given a sample"""
        raise NotImplementedError('In theaters Spring 2016')


class RequestReference:
    """Reference implementation of generic request

    For simplicity, built on top of a list of dicts.

    """
    def __init__(self, host=conf.conn_config['host'],
                 port=conf.conn_config['port'], sample=None, time=time.time(),
                 uid=str(uuid4()), state='active', seq_num=0):
        """Handles connection configuration to the service backend.
        Either initiate with a request or use purely as a client for requests.
        """
        self._server_path = 'http://{}:{}/' .format(host, port)
        self._request_list = []
        if sample:
            payload = dict(uid=uid, sample=sample['uid'], time=time,state=state,
                           seq_num=seq_num)
            print(self._server_path)
            print(payload)
            r = requests.post(self._server_path + 'request',
                            data=ujson.dumps(payload))
            r.raise_for_status()
            self._request_list.append(payload)

    def create_request(self, host=conf.conn_config['host'],
                 port=conf.conn_config['port'], sample=None, time=time.time(),
                 uid=str(uuid4()), state='active', seq_num=0, **kwargs):
        """

        Parameters
        ----------
        host: str
            Amostra server host machine
        port: int
            Amost server port on the host machine
        sample: dict, doct.Document
            The sample this reference refers to
        time: float
            Time request got created
        uid: str
            Unique identifier for
        state: str
            Enum 'active' or 'inactive' that displays the state of a request    
        seq_num: int
            Sequence number for creation of the request. Not indexed but can be updated

        Returns
        -------
        payload['uid']
            uid of the payload created
        """
        self._server_path = 'http://{}:{}/' .format(host, port)
        payload = dict(uid=uid, sample=sample['uid'], time=time,state=state,
                           seq_num=seq_num, **kwargs)
        r = requests.post(url=self._server_path + 'request',
                          data=ujson.dumps(payload))
        r.raise_for_status()
        return payload['uid']

    def find_request(self, **kwargs):
        r = requests.get(self._server_path + 'request',
                         params=ujson.dumps(kwargs))
        r.raise_for_status()
        content = ujson.loads(r.text)
        # add all content to local sample list
        self._request_list.extend(content)
        for c in content:
            yield Document('request', c)        

    def update(self, filter, update, host=conf.conn_config['host'], 
             port=conf.conn_config['port']):
        payload = dict(filter=filter, update=update)
        r = requests.put(url=self._server_path + 'request',
                          data=ujson.dumps(payload))