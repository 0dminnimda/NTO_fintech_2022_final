"""sugomA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import json
from ariadne import format_error


# from graphene_django.views import GraphQLView
from ariadne_django.views import GraphQLView
from django.contrib import admin
from django.http.response import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .AmogusApp.views import home
from .schema import schema, code_smell


def track(view):
    def wrapper(*args, **kwargs):
        response = view(*args, **kwargs)

        if isinstance(response, JsonResponse):
            data = json.loads(response.content)
            if "data" in data and "errors" in data:
                del data["data"]
            response = JsonResponse(data)  # json.dumps(data)
        else:
            code_smell.clear()

        return response

    wrapper.csrf_exempt = True
    return wrapper


mapping = {"A": {"message": "Authentication failed"}}


def my_format_error(error, debug: bool = False) -> dict:
    # # Create formatted error data
    # formatted = error.formatted
    # # Replace original error message with custom one
    # formatted["message"] = "INTERNAL SERVER ERROR"

    result = mapping.get(error.message, None)
    if result is not None:
        return result

    return format_error(error, debug)


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path('graphql', track(GraphQLView.as_view(
        schema=schema, error_formatter=my_format_error)), name='graphql'),
    # path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
