from django.shortcuts import render

# Create your views here.

def coffee_index(request):
    # Пример карточек сортов кофе
    coffee_cards = [
        {
            'name': 'Бурунди',
            'image': 'coffee/burundi.jpg',
            'desc': 'Яркая кислинка, фруктовые и ягодные ноты, насыщенный вкус.'
        },
        {
            'name': 'Эфиопия Йиргачефф',
            'image': 'coffee/ethiopia_yirgacheffe.jpg',
            'desc': 'Цветочные и цитрусовые оттенки, лёгкое тело, сладкое послевкусие.'
        },
        {
            'name': 'Колумбия Супремо',
            'image': 'coffee/colombia_supremo.jpg',
            'desc': 'Сбалансированная кислотность, ореховые и шоколадные ноты.'
        },
        {
            'name': 'Кения АА',
            'image': 'coffee/kenya_aa.jpg',
            'desc': 'Яркая кислинка, винные и ягодные оттенки, насыщенный аромат.'
        },
        {
            'name': 'Суматра Манделинг',
            'image': 'coffee/sumatra_mandheling.jpg',
            'desc': 'Плотное тело, землистые и пряные ноты, низкая кислотность.'
        },
        {
            'name': 'Бразилия Сантос',
            'image': 'coffee/brazil_santos.jpg',
            'desc': 'Мягкий вкус, ореховые и шоколадные оттенки, низкая кислотность.'
        },
        {
            'name': 'Гватемала Антигуа',
            'image': 'coffee/guatemala_antigua.jpg',
            'desc': 'Яркая кислинка, шоколадные и пряные ноты, насыщенный вкус.'
        },
    ]
    return render(request, 'coffee/coffee_index.html', {'coffee_cards': coffee_cards})
