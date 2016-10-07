import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from .models import *
from .serializers import *

''' Direct Views '''


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


''' Django Rest Framework ViewSets '''


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class BoardStateViewSet(viewsets.ModelViewSet):
    queryset = BoardState.objects.all()
    serializer_class = BoardStateSerializer


class StateTransitionViewSet(viewsets.ModelViewSet):
    queryset = StateTransition.objects.all()
    serializer_class = StateTransitionSerializer
