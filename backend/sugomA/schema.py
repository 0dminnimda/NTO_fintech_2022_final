import os
import secrets
import time

import eth_keys
from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)

from sugomA.AmogusApp.models import Authentication


class Hack:
    requested_auth: int
    auth_key: bytes
    successfull_auth: bool
    address: str

    def __init__(self):
        self.reset()

    def reset(self):
        self.requested_auth = 0
        self.auth_key = b"<invalid>"
        self.successfull_auth = False
        self.address = "<invalid>"

    def __str__(self):
        args = [self.requested_auth, self.auth_key, self.successfull_auth, self.address]
        return type(self).__name__ + "(" + ", ".join(map(str, args)) + ")"


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
    signature = eth_keys.KeyAPI.Signature(
        vrs=(signedMessage.v, signedMessage.r, signedMessage.s,))
    signer = signature.recover_public_key_from_msg(code_smell.auth_key)

    if signer == address and code_smell.requested_auth == 0:
        raise Exception("A")

    code_smell.successfull_auth = True
    code_smell.address = address
    authentications = Authentication.objects.filter(address=address)

    if len(authentications) == 0:
        return Authentication.objects.create(
            address=address, isLandlord=False)

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
