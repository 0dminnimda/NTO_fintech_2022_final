from ariadne import format_error
from graphql.error import GraphQLError


class sugomAException(Exception):
    message: str = "<none>"


class AuthenticationFailed(sugomAException):
    message = "Authentication failed"


class UnauthorizedAccess(sugomAException):
    message = "Authentication required"


class NotLandlordAccess(sugomAException):
    message = "This method is available only for the landlord"


class InvalidRoomParams(sugomAException):
    message = "The room area must be greater than zero"


class RoomNotFound(sugomAException):
    message = "Room with such ID not found"


def error_formatter(error: GraphQLError, debug: bool = False) -> dict:
    # formatted = error.formatted

    if isinstance(error.original_error, sugomAException):
        return {"message": error.original_error.message}

    return format_error(error, debug)
