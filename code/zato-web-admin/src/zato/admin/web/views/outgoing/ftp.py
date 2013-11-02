# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.ftp import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import OutgoingFTP

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-ftp'
    template = 'zato/outgoing/ftp.html'
    service_name = 'zato.outgoing.ftp.get-list'
    output_class = OutgoingFTP
    
    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'host', 'user', 'acct', 'timeout', 'port', 'dircache')
        output_repeated = True
    
    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'host', 'user', 'timeout', 'acct', 'port', 'dircache')
        output_required = ('id', 'name')
        
    def success_message(self, item):
        return 'Successfully {0} the outgoing FTP connection [{1}]'.format(self.verb, item.name)
    
class Create(_CreateEdit):
    url_name = 'out-ftp-create'
    service_name = 'zato.outgoing.ftp.create'

class Edit(_CreateEdit):
    url_name = 'out-ftp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.ftp.edit'

class Delete(_Delete):
    url_name = 'out-ftp-delete'
    error_message = 'Could not delete the outgoing FTP connection'
    service_name = 'zato.outgoing.ftp.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.ftp.change-password')
