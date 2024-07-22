from django.shortcuts import render  # type: ignore
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse  # type: ignore
from .forms import SearchForm
from .utils import process_data
import os
import json
import datetime
import pandas as pd
import openpyxl


def get_name(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        search = {}
        if form.is_valid():
            role = form.cleaned_data['role']
            search['role'] = role
            location = form.cleaned_data['location']
            search['location'] = location
            keywords = form.cleaned_data['keywords']
            search['keywords'] = keywords
            exclusion = form.cleaned_data['exclusion']
            search['exclusion'] = exclusion
            no_of_hits = form.cleaned_data['no_of_hits']
            search['no_of_hits'] = no_of_hits
            time_filter = form.cleaned_data['time_filter']
            search['time_filter'] = time_filter
            clearance = form.cleaned_data['clearance']
            search['clearance'] = clearance
            sponsorship = form.cleaned_data['sponsorship']
            search['sponsorship'] = sponsorship
            search_sites = form.cleaned_data['search_sites']
            search['search_sites'] = search_sites
            filtering = form.cleaned_data['filtering']
            search['filtering'] = filtering
            processed = process_data(search)
            if processed is True:
                filename = f'Job_Hunt.xlsx'
                response_data = {
                    'status': 'success',
                    'download_url': f'/download/{filename}'
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'status': 'error', 'message': f'{processed}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
    else:
        form = SearchForm()
    return render(request, 'myapp/search.html', {'form': form})


def download_file(request, filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment;filename={filename}'
            return response
    else:
        return HttpResponse('File not found', status=404)
