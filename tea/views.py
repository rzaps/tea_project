from django.shortcuts import render
from supabase_client import supabase  # импорт клиента Supabase
from django.http import HttpRequest
from django.http import JsonResponse

def teas_api(request):
    response = supabase.table('teas').select('*').execute()
    teas = response.data
    return JsonResponse(teas, safe=False)

def tea_list(request: HttpRequest):
    type_filter = request.GET.get('type')
    region_filter = request.GET.get('region')
    taste_filter = request.GET.get('taste')

    # ⚠️ Важно: сначала .select(), потом .eq()
    query = supabase.table('teas').select('*')

    if type_filter:
        query = query.eq('type', type_filter)
    if region_filter:
        query = query.eq('region', region_filter)
    if taste_filter:
        query = query.eq('taste', taste_filter)

    # Выполняем запрос
    response = query.execute()
    teas = response.data

    # Все чаи для получения уникальных значений фильтров
    all_teas = supabase.table('teas').select('type', 'region', 'taste').execute().data

    types = sorted(set(t['type'] for t in all_teas if t['type']))
    regions = sorted(set(t['region'] for t in all_teas if t['region']))
    tastes = sorted(set(t['taste'] for t in all_teas if t['taste']))

    return render(request, 'teas_list.html', {
        'teas': teas,
        'types': types,
        'regions': regions,
        'tastes': tastes,
    })
