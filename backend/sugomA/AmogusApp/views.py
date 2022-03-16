from django.shortcuts import render
from django.http import HttpResponse


# def MetaMask_auth(request):
def home(request):
    return render(request, "home.html")


def check(request):
    response = render(request, "home.html")

    # cookies
    # a = int(request.COOKIES.get("a", "0"))
    # print(a)
    # response.set_cookie("a", str(a + 1))  # set_signed_cookie

    # session
    a = request.session.get("a", 0)
    print(a)
    request.session["a"] = a + 1

    return response
