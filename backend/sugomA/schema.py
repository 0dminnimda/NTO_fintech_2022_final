import os
import secrets
import time
from dataclasses import _FIELDS, Field, dataclass

import eth_keys
from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)

from sugomA.AmogusApp.models import Authentication


@dataclass
class Hack:
    requested_auth: int = 0
    auth_message: str = "<invalid>"
    successfull_auth: bool = False
    address: str = "<invalid>"

    def reset(self):
        for name in getattr(self, _FIELDS).keys():
            self.reset_attr(name)

    def reset_attr(self, attr: str) -> None:
        field: Field = getattr(self, _FIELDS)[attr]
        setattr(self, field.name, field.default)

    # storage: dict
    # def __getattr__(self, name: str):
    #     self.storage


code_smell = Hack()


type_defs = """
type Query {
    authentication: Authentication
    rooms: [Room!]!
    room(id: ID!): Room!
}

type Mutation {
    requestAuthentication(address: String!): String!
    authenticate(
        address: String!
        signedMessage: InputSignature!
    ): Authentication!

    createRoom(room: InputRoom!): Room!
    editRoom(id: ID!, room: InputRoom!): Room!
    setRoomContractAddress(id: ID!, contractAddress: String): Room!
    setRoomPublicName(id: ID!, publicName: String): Room!
    removeRoom(id: ID!): Room!
}

# Authentication
type Authentication {
    address: String!
    isLandlord: Boolean!
}

# Rooms
type Room {
    id: ID!
    internalName: String!
    area: Float!
    location: String!

    contractAddress: String
    publicName: String
}

# Input
input InputRoom {
    internalName: String!
    area: Float!
    location: String!
}

input InputSignature {
    v: String!
    r: String!
    s: String!
}
"""


query = QueryType()


@query.field("authentication")
def resolve_authentication(_, info):
    if not code_smell.successfull_auth:
        return None

    return Authentication.objects.get(address=code_smell.address)


mutation = MutationType()


@mutation.field("requestAuthentication")
def resolve_request_authentication(_, info, address):
    code_smell.requested_auth = 2
    key = str(time.time()) + "_" + secrets.token_urlsafe(30)
    code_smell.auth_key = key.encode('utf-8')
    return key


@mutation.field("authenticate")
def resolve_authenticate(_, info, address, signedMessage):
    signer = address

    if signer == address and code_smell.requested_auth == 0:
        raise Exception("A")

    code_smell.successfull_auth = True
    code_smell.address = address
    authentications = Authentication.objects.filter(address=address)

    if len(authentications) != 0:  # should be 1
        return authentications[0]

    return Authentication.objects.create(
        address=address, isLandlord=os.environ.get("LANDLORD_ADDRESS", False))


# authentication = ObjectType("Authentication")


# @authentication.field("address")
# def resolve_address(root, info):
#     return root.address


# @authentication.field("isLandlord")
# def resolve_is_landlord(root, info):
#     return root.isLandlord


schema = make_executable_schema(
    gql(type_defs), query, mutation,
    # authentication
)  # type: ignore
