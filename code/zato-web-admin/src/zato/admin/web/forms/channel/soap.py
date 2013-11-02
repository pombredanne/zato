# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class DefinitionForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    url_pattern = forms.CharField(widget=forms.TextInput(attrs={"class":"required", "style":"width:90%"}))
