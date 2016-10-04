from django.shortcuts import render


def index(request):
    context = dict()
    return render(request, 'core/index.html', context=context)