from django.shortcuts import render

def beer_index(request):
    beer_cards = [
        {
            'name': 'Пилснер',
            'image': 'beer/pilsner.jpg',
            'desc': 'Светлое, освежающее пиво с выраженной хмелевой горчинкой.'
        },
        {
            'name': 'ИПА (India Pale Ale)',
            'image': 'beer/ipa.jpg',
            'desc': 'Ароматное пиво с яркой горчинкой и цитрусовыми нотами.'
        },
        {
            'name': 'Стаут',
            'image': 'beer/stout.jpg',
            'desc': 'Тёмное пиво с оттенками кофе, шоколада и карамели.'
        },
        {
            'name': 'Вайцен',
            'image': 'beer/weizen.jpg',
            'desc': 'Пшеничное пиво с фруктовыми и пряными нотами.'
        },
        {
            'name': 'Ламбик',
            'image': 'beer/lambic.jpg',
            'desc': 'Кисловатое бельгийское пиво, часто с добавлением фруктов.'
        },
        {
            'name': 'Портер',
            'image': 'beer/porter.jpg',
            'desc': 'Тёмное пиво с насыщенным вкусом и карамельными оттенками.'
        },
        {
            'name': 'Саур',
            'image': 'beer/sour.jpg',
            'desc': 'Кислое пиво с фруктовыми и ягодными нотами.'
        },
    ]
    return render(request, 'beer/beer_index.html', {'beer_cards': beer_cards}) 