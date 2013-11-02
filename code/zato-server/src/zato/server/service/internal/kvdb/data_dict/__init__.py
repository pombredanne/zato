# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common import KVDB, ZatoException
from zato.common.util import multikeysort, translation_name
from zato.server.service.internal import AdminService

class DataDictService(AdminService):
    def __init__(self, *args, **kwargs):
        super(DataDictService, self).__init__(*args, **kwargs)
        self._dict_items = []
        
    def _name(self, system1, key1, value1, system2, key2):
        return translation_name(system1, key1, value1, system2, key2)

    def _get_dict_item(self, id):
        """ Returns a dictionary entry by its ID.
        """
        for item in self._get_dict_items():
            if item['id'] == str(id):
                return item
        else:
            msg = 'Could not find the dictionary by its ID:[{}}]'.format(id)
            raise ZatoException(self.cid, msg)

    def _get_dict_items_raw(self):
        """ Yields dictionary items without formatting them into Python dictionaries.
        """
        for id, item in self.server.kvdb.conn.hgetall(KVDB.DICTIONARY_ITEM).items():
            yield id, item
        
    def _get_dict_items(self):
        """ Yields nicely formatted dictionary items defined in the KVDB.
        """
        if not self._dict_items:
            for id, item in self.server.kvdb.conn.hgetall(KVDB.DICTIONARY_ITEM).items():
                system, key, value = item.decode('utf-8').split(KVDB.SEPARATOR)
                self._dict_items.append({'id':str(id), 'system':system, 'key':key, 'value':value})
            self._dict_items = multikeysort(self._dict_items, ['system', 'key', 'value'])

        for item in self._dict_items:
            yield item
            
    def _get_dict_item_id(self, system, key, value):
        """ Returns a dictionary entry ID by its system, key and value.
        """
        for item in self._get_dict_items():
            if item['system'] == system and item['key'] == key and item['value'] == value:
                return item['id']
            
    def _get_translations(self):
        """ Yields nicely formatted translations defined in the KVDB.
        """
        for item in self.server.kvdb.conn.keys(KVDB.TRANSLATION + KVDB.SEPARATOR + '*'):
            vals = self.server.kvdb.conn.hgetall(item)
            item = item.decode('utf-8').split(KVDB.SEPARATOR)
            yield {'system1':item[1], 'key1':item[2], 'value1':item[3], 'system2':item[4], 
                   'key2':item[5], 'id':str(vals.get('id')), 'value2':vals.get('value2').decode('utf-8'),
                   'id1':str(vals.get('id1')), 'id2':str(vals.get('id2')),}
