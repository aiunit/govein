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
    context['state_list'] = BoardState.objects.all()[:20]
    return render(request, 'core/index.html', context=context)


@login_required
@require_POST
def submit(request):
    import json
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


def preview(request, pk):
    bs = BoardState.objects.get(id=pk)
    return HttpResponse(
        bs.get_preview_image_bytes(),
        content_type='image/gif',
    )
