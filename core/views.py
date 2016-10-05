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
    import io
    from PIL import Image, ImageDraw

    bs = BoardState.objects.get(id=pk)

    sz = 95
    board_fill = (222, 184, 135)
    image = Image.new('RGB', (sz, sz), board_fill)
    draw = ImageDraw.Draw(image)

    # Board lines
    line_fill = (0, 0, 0)
    for i in range(2, sz, 5):
        draw.line((2, i, 92, i), fill=line_fill)
        draw.line((i, 2, i, 92), fill=line_fill)

    # Stars
    star_fill = (111, 92, 68)
    for i in range(2 + 5 * 3, sz, 5 * 6):
        for j in range(2 + 5 * 3, sz, 5 * 6):
            # draw.point((i, j), fill=(0,) * 3)
            draw.point((i - 1, j - 1), fill=star_fill)
            draw.point((i + 1, j - 1), fill=star_fill)
            draw.point((i - 1, j + 1), fill=star_fill)
            draw.point((i + 1, j + 1), fill=star_fill)

    # Stones
    grid = bs.to_grid()
    for i in range(19):
        for j in range(19):
            if not grid[i][j]:
                continue
            fill = [None, (0,) * 3, (255,) * 3][grid[i][j]]
            xy = (j * 5, i * 5, j * 5 + 4, i * 5 + 4)
            draw.ellipse(xy, fill)

    # Output the image streaming
    fs = io.BytesIO()
    image.save(fs, 'gif')
    return HttpResponse(
        fs.getbuffer(),
        content_type='image/gif',
    )
