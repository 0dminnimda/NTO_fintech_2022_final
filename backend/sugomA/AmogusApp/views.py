from django.shortcuts import render
from django.http import HttpResponse


# def MetaMask_auth(request):
def home(request):
    return render(request, 'home.html')
    # return HttpResponse("You're voting on question")
