# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class _Base(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    service = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))
    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:30%; height:19px'}))
    
class OneTimeSchedulerJobForm(_Base):
    pass

class IntervalBasedSchedulerJobForm(_Base):
    # Attributes specific to interval-based jobs.
    weeks = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    days = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    hours = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    minutes = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    seconds = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:30%; height:19px'}))
    repeats = forms.CharField(widget=forms.TextInput(attrs={'style':'width:8%'}))
    
class CronStyleSchedulerJobForm(_Base):
    cron_definition = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
