from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required  # больше не нужен
from backend.supabase_client import supabase
import json

@require_GET
def get_comments(request, object_type, object_id):
    comments = supabase.table('comments').select('id, text, created_at, user_id').eq('object_type', object_type).eq('object_id', str(object_id)).order('created_at').execute().data
    # Получаем email для каждого user_id
    user_ids = list({c['user_id'] for c in comments if c.get('user_id')})
    emails = {}
    if user_ids:
        users_data = supabase.table('users').select('id, email').in_('id', user_ids).execute().data
        emails = {u['id']: u['email'] for u in users_data}
    for c in comments:
        c['email'] = emails.get(c.get('user_id'), 'Аноним')
    return JsonResponse(comments, safe=False)

@csrf_exempt
@require_POST
def add_comment(request, object_type, object_id):
    print('DEBUG session:', dict(request.session))
    supabase_user_id = request.session.get('supabase_user_id')
    if not supabase_user_id:
        print('DEBUG: Not authenticated')
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    user_id = str(supabase_user_id)
    data = json.loads(request.body)
    text = data.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Комментарий не может быть пустым'}, status=400)
    supabase.table('comments').insert({
        'object_type': object_type,
        'object_id': str(object_id),  # Преобразуем UUID в строку
        'user_id': user_id,
        'text': text,
    }).execute()
    print('DEBUG: Comment added')
    return JsonResponse({'success': True}) 