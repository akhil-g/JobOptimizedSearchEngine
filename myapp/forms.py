from django import forms  # type: ignore
from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)


class SearchForm(forms.Form):
    role = forms.CharField(
        label='Role',
        max_length=100,
        help_text='Enter your desired role'
    )
    location = forms.CharField(
        label='Location',
        max_length=100,
        help_text='Enter your desired location',
        required=False
    )
    keywords = forms.CharField(
        label='Keywords',
        max_length=100,
        help_text='Enter your keywords wanted to include such as `Python Kubernetes` in space separated format',
        required=False
    )
    exclusion = forms.CharField(
        label='Exclusion',
        max_length=100,
        help_text='Enter your keywords wanted to exclude such as `react angular` in space separated format',
        required=False
    )
    no_of_hits = forms.IntegerField(
        label='Hits per Site',
        min_value=1,
        max_value=20,
        initial=5,
        help_text='Enter your no of hits per site',
        required=False
    )
    time_filter = forms.ChoiceField(
        label='Time filter',
        choices=[('Past hour', 'Past hour'), ('Past day', 'Past day'), ('Past week', 'Past week'),
                 ('Past month', 'Past month'), ('Past year', 'Past year')]
    )
    clearance = forms.ChoiceField(
        label='Security Clearance',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.CheckboxInput,
        help_text='Select if you like to exclude security clearance jobs',
        required=False
    )
    sponsorship = forms.ChoiceField(
        label='Sponsorship',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.CheckboxInput,
        help_text='Select if you like to exclude jobs which do not provide sponsorship',
        required=False
    )
    search_sites = forms.MultipleChoiceField(
        label='Search Sites',
        choices=[('site:greenhouse.io', 'greenhouse.io'), ('site:lever.co', 'lever.co'), ('site:dover.com', 'dover.com'), ('site:jobs.*', 'jobs.*'), ('site:careers.*', 'careers.*'), ('site:oraclecloud.com', 'oraclecloud.com'),
                 ('site:myworkdayjobs.com', 'myworkdayjobs.com'), ('site:icims.com', 'icims.com'), ('site:notion.site', 'notion.site')],
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )
    filtering = forms.ChoiceField(
        label='Auto filter',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.CheckboxInput,
        help_text='Select if you like to filter the requirements automatically',
        required=False
    )
