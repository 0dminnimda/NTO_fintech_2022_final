import json
import os
import secrets
import time

from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)
from eth_account import Account
from eth_account.messages import encode_defunct

from sugomA.AmogusApp.models import Authentication


class Hack:
    storage: dict

    attrs = {
        "requested_auth": 0,
        "auth_message": "<invalid>",
        "successfull_auth": False,
        "address": "<invalid>",
    }

    def __init__(self, storage):
        self.storage = storage
        self.reset()

    def reset(self):
        for name in self.attrs.keys():
            self.reset_attr(name)

    def reset_attr(self, name):
        default = self.attrs[name]
        self[name] = default
        return default

    def __getitem__(self, name, default=object()):
        result = self.storage.get(name, default)
        if result is default:
            return self.reset_attr(name)
        if type(self.attrs[name]) is not str:
            return json.loads(result)
        return result

    def __setitem__(self, name, value):
        if type(self.attrs[name]) is not str:
            value = json.dumps(value)
        self.storage[name] = value

    def __str__(self):
        args = [f"{name}={self[name]}" for name in self.attrs.keys()]
        return f"{type(self).__name__}({self.storage}, {{{', '.join(args)}}})"


code_smell = Hack({})


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
    if not code_smell["successfull_auth"]:
        return None

    return Authentication.objects.get(address=code_smell["address"])


mutation = MutationType()


@mutation.field("requestAuthentication")
def resolve_request_authentication(_, info, address):
    code_smell.reset()
    code_smell["requested_auth"] = 2

    message = str(time.time()) + "_" + secrets.token_urlsafe(30)
    code_smell["auth_message"] = message

    # user-side code to generate accurate authenticate() arguments:
    # private_key = "0x" + secrets.token_hex(32)
    # acc = Account.from_key(private_key)
    # sig = Account.sign_message(encode_defunct(text=message), private_key)
    # vrs = list(map(hex, (sig.v, sig.r, sig.s)))
    # print(f"{private_key=}, {acc.address=}, {vrs=}")

    return message


@mutation.field("authenticate")
def resolve_authenticate(_, info, address, signedMessage):
    recovered_address = Account.recover_message(
        encode_defunct(text=code_smell["auth_message"]),
        vrs=[int(i, 16) for i in signedMessage.values()])

    if recovered_address != address or code_smell["requested_auth"] != 1:
        code_smell.reset()
        raise Exception("A")

    code_smell["successfull_auth"] = True
    code_smell["address"] = address
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
