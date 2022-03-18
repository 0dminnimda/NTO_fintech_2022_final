import json
from django.shortcuts import render
from django.http import HttpResponse
from ..schema import code_smell


def home(request):
    count = str(code_smell["count_home_requests"])
    code_smell["count_home_requests"] += 1
    print("START\n", (count*10 + "\n") * 10)

    return render(request, "home.html")


def check(request):
    # if request.method == "POST":
    #     print(json.loads(request.body))

    response = render(request, "home.html")

    # cookies
    a = int(request.COOKIES.get("a", "0"))
    print(a)
    response.set_cookie("a", str(a + 1))  # set_signed_cookie

    # code_smell.storage = request.COOKIES
    # print(request.COOKIES)
    # print(code_smell)
    # code_smell["a"] += 1

    # for n, v in code_smell.storage.items():
    #     response.set_cookie(n, v)

    # session
    # print(request.session.session_key)
    # a = request.session.get("a", 0)
    # print(a)
    # request.session["a"] = a + 1

    return response
