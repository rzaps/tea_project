from django.shortcuts import render

def wine_index(request):
    wine_cards = [
        {
            'name': 'Каберне Совиньон',
            'image': 'wine/cabernet_sauvignon.jpg',
            'desc': 'Плотное красное вино с нотами чёрной смородины, специй и дуба.'
        },
        {
            'name': 'Мерло',
            'image': 'wine/merlot.jpg',
            'desc': 'Мягкое, фруктовое красное вино с бархатистыми танинами.'
        },
        {
            'name': 'Пино Нуар',
            'image': 'wine/pinot_noir.jpg',
            'desc': 'Лёгкое красное вино с ароматами вишни, малины и земли.'
        },
        {
            'name': 'Шардоне',
            'image': 'wine/chardonnay.jpg',
            'desc': 'Белое вино с нотами яблока, цитрусов и сливочного масла.'
        },
        {
            'name': 'Совиньон Блан',
            'image': 'wine/sauvignon_blanc.jpg',
            'desc': 'Свежий вкус, ароматы зелёного яблока, трав и цитрусов.'
        },
        {
            'name': 'Рислинг',
            'image': 'wine/riesling.jpg',
            'desc': 'Ароматное белое вино с нотами персика, абрикоса и цветов.'
        },
        {
            'name': 'Сира',
            'image': 'wine/syrah.jpg',
            'desc': 'Насыщенное красное вино с оттенками чёрного перца, ягод и шоколада.'
        },
    ]
    return render(request, 'wine/wine_index.html', {'wine_cards': wine_cards}) 