from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .models import *


def index(request):
    context = dict()
    key = request.GET.get('id', 0)
    context['state'] = BoardState.objects.filter(id=key).first()
    context['state_list'] = BoardState.objects.all()[:20]
    return render(request, 'core/index.html', context=context)


@require_POST
def submit(request):
    import json
    data = json.loads(request.body.decode())
    bs = BoardState.from_grid(
        data.get('grid'),
        data.get('rob'),
    )
    # print(str(bs))
    return HttpResponse(json.dumps(dict(
        id=bs.id
    )))
