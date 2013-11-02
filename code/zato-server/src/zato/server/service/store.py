# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import imp, inspect, logging, os
from datetime import datetime
from hashlib import sha256
from importlib import import_module
from traceback import format_exc
from uuid import uuid4

# pip
from pip.download import is_archive_file

# anyjson
from anyjson import dumps

# PyYAML
try:
    from yaml import CDumper  # Looks awkward but
    Dumper = CDumper          # it's to make import checkers happy
except ImportError:
    from yaml import Dumper   # ditto
    Dumper = Dumper
    
# Spring Python
from springpython.context import InitializingObject

# Zato
from zato.common import DONT_DEPLOY_ATTR_NAME, NoDistributionFound, SourceInfo
from zato.common.util import decompress, deployment_info, fs_safe_now, is_python_file, \
    TRACE1, visit_py_source, visit_py_source_from_distribution
from zato.server.service import Service
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

def get_service_name(class_obj):
    """ Return the name of a service which will be either given us explicitly
    via the 'name' attribute or it will be a concatenation of the name of the
    class and its module's name.
    """
    return getattr(class_obj, 'name', '%s.%s' % (class_obj.__module__, class_obj.__name__))

class ServiceStore(InitializingObject):
    """ A store of Zato services.
    """
    def __init__(self, services=None, service_store_config=None, odb=None):
        self.services = services
        self.service_store_config = service_store_config
        self.odb = odb
        self.id_to_impl_name = {}
        self.name_to_impl_name = {}

    def _invoke_hook(self, object_, hook_name):
        """ A utility method for invoking various service's hooks.
        """
        try:
            hook = getattr(object_, hook_name)
            hook()
        except Exception:
            msg = 'Error while invoking [%s] on service [%s] ' \
                ' e:[%s]' % (hook_name, object_, format_exc())
            logger.error(msg)

    def new_instance(self, class_name):
        """ Returns a new instance of a service of the given impl name.
        """
        return self.services[class_name]['service_class']()
        
    def new_instance_by_id(self, service_id):
        impl_name = self.id_to_impl_name[service_id]
        return self.new_instance(impl_name)
        
    def new_instance_by_name(self, name):
        impl_name = self.name_to_impl_name[name]
        return self.new_instance(impl_name)

    def service_data(self, impl_name):
        """ Returns all the service-related data.
        """
        return self.services[impl_name]
    
    def decompress(self, archive, work_dir):
        """ Decompresses an archive into a randomly named directory.
        """
        # 6 characters will do, we won't deploy millions of services
        # in the very same (micro-)second after all
        rand = uuid4().hex[:6] 
        
        dir_name = os.path.join(work_dir, '{}-{}'.format(fs_safe_now(), rand), os.path.split(archive)[1])
        os.makedirs(dir_name)
        
        # .. unpack the archive into it ..
        decompress(archive, dir_name)
        
        # .. and return the name of the newly created directory so that the
        # rest of the machinery can pick the services up
        return dir_name

    def import_services_from_anywhere(self, items, base_dir, work_dir=None):
        """ Imports services from any of the supported sources, be it module names,
        individual files, directories or distutils2 packages (compressed or not).
        """
        for item_name in items:
            logger.debug('About to import services from:[%s]', item_name)
            
            is_internal = item_name.startswith('zato')
            
            # distutils2 archive, decompress and import from the newly created directory ..
            if is_archive_file(item_name):
                new_path = self.decompress(item_name, work_dir)
                self.import_services_from_dist2_directory(new_path)
            
            # .. a regular directory or a Distutils2 one ..
            elif os.path.isdir(item_name):
                try:
                    self.import_services_from_directory(item_name, base_dir, True)
                except NoDistributionFound, e:
                    msg = 'Caught an exception e=[{}]'.format(format_exc(e))
                    logger.log(TRACE1, msg)
                    self.import_services_from_directory(item_name, base_dir, False)
            
            # .. a .py/.pyw
            elif is_python_file(item_name):
                self.import_services_from_file(item_name, is_internal, base_dir)
            
            # .. must be a module object
            else:
                self.import_services_from_module(item_name, is_internal)

    def import_services_from_file(self, file_name, is_internal, base_dir):
        """ Imports all the services from the path to a file.
        """
        if not os.path.isabs(file_name):
            file_name = os.path.normpath(os.path.join(base_dir, file_name))

        if not os.path.exists(file_name):
            raise ValueError("Could not import services, path:[{}] doesn't exist".format(file_name))
        
        _, mod_file = os.path.split(file_name)
        mod_name, _ = os.path.splitext(mod_file)
        
        # Delete compiled bytecode if it exists so that imp.load_source 
        # actually picks up the source module
        for suffix in('c', 'o'):
            path = file_name + suffix
            if os.path.exists(path):
                os.remove(path)
        
        try:
            mod = imp.load_source(mod_name, file_name)
        except Exception, e:
            msg = 'Could not load source mod_name:[{}] file_name:[{}], e:[{}]'.format(
                mod_name, file_name, format_exc(e))
            logger.error(msg)
        else:
            self._visit_module(mod, is_internal, file_name)
        
    def import_services_from_directory(self, dir_name, base_dir, dist2):
        """ dir_name points to a directory. 
        
        If dist2 is True, the directory is assumed to be a Distutils2 one and its
        setup.cfg file is read and all the modules from packages pointed to by the 
        'files' section are scanned for services.
        
        If dist2 is False, this will be treated as a directory with a flat list
        of Python source code to import, as is the case with services that have
        been hot-deployed.
        """
        func = visit_py_source_from_distribution if dist2 else visit_py_source
        for py_path in func(dir_name):
            self.import_services_from_file(py_path, False, base_dir)
        
    def import_services_from_module(self, mod_name, is_internal):
        """ Imports all the services from a module specified by the given name.
        """
        mod = import_module(mod_name)
        self._visit_module(mod, is_internal, inspect.getfile(mod))
        
    def _should_deploy(self, name, item):
        """ Is an object something we can deploy on a server?
        """
        try:
            if issubclass(item, Service):
                if item is not AdminService and item is not Service:
                    if not hasattr(item, DONT_DEPLOY_ATTR_NAME):
                        return True
        except TypeError, e:
            # Ignore non-class objects passed in to issubclass
            logger.log(TRACE1, 'Ignoring exception, name:[{}], item:[{}], e:[{}]'.format(name, item, format_exc(e)))
            
    def _get_source_code_info(self, mod):
        """ Returns the source code of and the FS path to the given module.
        """
        si = SourceInfo()
        try:
            file_name = mod.__file__
            if file_name[-1] in('c', 'o'):
                file_name = file_name[:-1]

            # We would've used inspect.getsource(mod) hadn't it been apparently using
            # cached copies of the source code
            si.source = open(file_name, 'rb').read()
            
            si.path = inspect.getsourcefile(mod)
            si.hash = sha256(si.source).hexdigest()
            si.hash_method = 'SHA-256'
            
        except IOError, e:
            logger.log(TRACE1, 'Ignoring IOError, mod:[{}], e:[{}]'.format(mod, format_exc(e)))
            
        return si
                
    def _visit_module(self, mod, is_internal, fs_location):
        """ Actually imports services from a module object.
        """
        try:
            for name in sorted(dir(mod)):
                item = getattr(mod, name)
                if self._should_deploy(name, item):
                    
                    should_add = item.before_add_to_store(logger)
                    if should_add:
                        
                        timestamp = datetime.utcnow().isoformat()
                        depl_info = deployment_info('service-store', item, timestamp, fs_location)
                        name = item.get_name()
                        impl_name = item.get_impl_name()
                        
                        self.services[impl_name] = {}
                        self.services[impl_name]['name'] = name
                        self.services[impl_name]['deployment_info'] = depl_info
                        self.services[impl_name]['service_class'] = item
                        
                        si = self._get_source_code_info(mod)
                        
                        service_id, is_active, slow_threshold = self.odb.add_service(
                            name, impl_name, is_internal, timestamp, dumps(str(depl_info)), si)
                        
                        self.services[impl_name]['is_active'] = is_active
                        self.services[impl_name]['slow_threshold'] = slow_threshold
                        
                        self.id_to_impl_name[service_id] = impl_name
                        self.name_to_impl_name[name] = impl_name
                        
                        logger.debug('Imported service:[{}]'.format(name))
                        
                        item.after_add_to_store(logger)
                    else:
                        msg = 'Skipping [{}] from [{}], should_add:[{}] is not True'.format(
                            item, fs_location, should_add)
                        logger.info(msg)
        except Exception, e:
            msg = 'Exception while visit mod:[{}], is_internal:[{}], fs_location:[{}], e:[{}]'.format(
                mod, is_internal, fs_location, format_exc(e))
            logger.error(msg)
                
if __name__ == '__main__':
    store = ServiceStore()
    store.import_services_from_directory('/home/dsuch/tmp/zato-sample-project1')
