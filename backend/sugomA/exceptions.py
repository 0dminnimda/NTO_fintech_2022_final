from ariadne import format_error
from graphql.error import GraphQLError


class sugomAException(Exception):
    message: str = "<none>"


class AuthenticationFailed(sugomAException):
    message = "Authentication failed"


class InvalidRoomParams(sugomAException):
    message = "The room area must be greater than zero"


def error_formatter(error: GraphQLError, debug: bool = False) -> dict:
    # formatted = error.formatted

    if isinstance(error.original_error, sugomAException):
        return {"message": error.original_error.message}

    return format_error(error, debug)
