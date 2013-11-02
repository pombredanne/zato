# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# pika
from pika.spec import FRAME_MAX_SIZE, PORT

# Django
from django import forms

# Zato
from zato.common.util import make_repr


class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    port = forms.CharField(initial=PORT, widget=forms.TextInput(attrs={'style':'width:20%'}))
    vhost = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:50%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    frame_max = forms.CharField(initial=FRAME_MAX_SIZE, widget=forms.TextInput(attrs={'style':'width:20%'}))
    heartbeat = forms.CharField(initial=0, widget=forms.TextInput(attrs={'style':'width:10%'}))

    def __repr__(self):
        return make_repr(self)
    
class EditForm(CreateForm):
    pass
