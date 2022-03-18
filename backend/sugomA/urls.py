import json
from typing import cast

from ariadne.constants import DATA_TYPE_JSON, DATA_TYPE_MULTIPART
from ariadne.exceptions import HttpBadRequestError
from ariadne.file_uploads import combine_multipart_data
from ariadne.graphql import graphql_sync
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphql import GraphQLSchema

from .exceptions import error_formatter
from .AmogusApp.views import check, home
from .schema import code_smell, schema


def extract_data_from_request(request: HttpRequest):
    content_type = request.content_type or ""
    content_type = content_type.split(";")[0]

    if content_type == DATA_TYPE_JSON:
        try:
            return json.loads(request.body)
        except (TypeError, ValueError) as ex:
            raise HttpBadRequestError(
                "Request body is not a valid JSON") from ex
    if content_type == DATA_TYPE_MULTIPART:
        try:
            operations = json.loads(request.POST.get("operations", "{}"))
        except (TypeError, ValueError) as ex:
            raise HttpBadRequestError(
                "Request 'operations' multipart field is not a valid JSON") from ex
        try:
            files_map = json.loads(request.POST.get("map", "{}"))
        except (TypeError, ValueError) as ex:
            raise HttpBadRequestError(
                "Request 'map' multipart field is not a valid JSON") from ex

        return combine_multipart_data(operations, files_map, request.FILES)

    raise HttpBadRequestError(
        "Posted content must be of type {} or {}".format(
            DATA_TYPE_JSON, DATA_TYPE_MULTIPART))


def get_context_for_request(context_value, request: HttpRequest):
    if callable(context_value):
        return context_value(request)
    return context_value or {"request": request}


def get_extensions_for_request(extensions, request: HttpRequest, context):
    if callable(extensions):
        return extensions(request, context)
    return extensions


def get_kwargs_graphql(request: HttpRequest) -> dict:
    context_value = get_context_for_request(None, request)
    extensions = get_extensions_for_request(None, request, context_value)

    # http_method_names = ["get", "post", "options"]
    # template_name = "ariadne_django/graphql_playground.html"
    # playground_options: Optional[dict] = None
    # schema: Optional[GraphQLSchema] = None

    return {
        "context_value": context_value,
        "root_value": None,
        "validation_rules": None,
        "debug": settings.DEBUG,
        "introspection": True,
        "logger": None,
        "error_formatter": error_formatter,
        "extensions": extensions,
        "middleware": None,
    }


@csrf_exempt
def graphql_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, "home.html")

    try:
        data = extract_data_from_request(request)
    except HttpBadRequestError as error:
        return HttpResponseBadRequest(error.message)

    print("\n" + "#"*5, "request", data)

    code_smell.storage = request.COOKIES

    success, result = graphql_sync(
        cast(GraphQLSchema, schema), data, **get_kwargs_graphql(request))
    status_code = 200 if success else 400

    if code_smell["requested_auth"] > 0:
        code_smell["requested_auth"] -= 1

    response = JsonResponse(result, status=status_code)

    print("#"*5, "response", result)

    for n, v in code_smell.storage.items():
        response.set_cookie(n, v)

    return response


@csrf_exempt
def rooms_view(request: HttpRequest):
    return render(request, "rooms.html")


@csrf_exempt
def rooms_create_view(request: HttpRequest):
    return render(request, "rooms_create.html")


@csrf_exempt
def room_view(request: HttpRequest, room_id):
    print('ROOM:', room_id)
    return render(request, "room.html")


urlpatterns = [
    path("", csrf_exempt(home)),
    path("admin/", admin.site.urls),
    path('graphql', graphql_view, name='graphql'),
    path('rooms', rooms_view),
    path('rooms/create', rooms_create_view),
    path('room/<int:room_id>', room_view),
    path("check", csrf_exempt(check)),
]
