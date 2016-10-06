import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .models import *


@login_required
def index(request):
    context = dict()
    key = request.GET.get('id', 0)
    context['state'] = BoardState.objects.filter(id=key).first()
    context['state_list'] = BoardState.objects.order_by('data')[:100]
    return render(request, 'core/index.html', context=context)


@login_required
@require_POST
def submit(request):
    data = json.loads(request.body.decode())
    bs = BoardState.from_grid(
        grid=data.get('grid'),
        rob=data.get('rob'),
        author=request.user,
    )
    # print(str(bs))
    return HttpResponse(json.dumps(dict(
        id=bs.id
    )))


@require_POST
def spy(request):
    """
    SPY the state by submitting the grid
    :param request:
    :return:
    """
    params = json.loads(request.body.decode())
    data, rob = BoardState.get_normalization(
        data=BoardState.get_data_from_grid(params.get('grid')),
        rob=params.get('rob'),
    )

    key = BoardState.get_key_from_data(data, rob)

    return HttpResponse(json.dumps(dict(
        id=key,
        store=BoardState.objects.filter(id=key).exists(),
    )))


def preview(request, pk):
    bs = BoardState.objects.get(id=pk)
    return HttpResponse(
        bs.get_preview_image_bytes(),
        content_type='image/gif',
    )
