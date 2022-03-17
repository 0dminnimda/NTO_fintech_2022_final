import os
import secrets
import time
from dataclasses import _FIELDS, Field, dataclass

from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)
from eth_account import Account
from eth_account.messages import encode_defunct

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

    message = str(time.time()) + "_" + secrets.token_urlsafe(30)
    code_smell.auth_message = message

    # user-side code to generate accurate authenticate() arguments:
    # private_key = "0x" + secrets.token_hex(32)
    # acc = Account.from_key(private_key)
    # sig = Account.sign_message(encode_defunct(text=message), private_key)
    # vrs = list(map(hex, (sig.v, sig.r, sig.s)))
    # print(f"{private_key=}, {acc.address=}, {vrs=}")

    return message


@mutation.field("authenticate")
def resolve_authenticate(_, info, address, signedMessage):
    # sig = eth_keys.KeyAPI.Signature(signature_bytes=(eth_keys.KeyAPI.PublicKey.from_compressed_bytes(chr(0x02).encode("utf-8")) + chr(0x02)).to_bytes())
    # signature = eth_keys.KeyAPI.Signature(vrs=(
    #     int(signedMessage["v"], 16),
    #     int(signedMessage["r"], 16),
    #     int(signedMessage["s"], 16)))
    # public_key = signature.recover_public_key_from_msg(code_smell.auth_message)
    # print(public_key, address)
    # (int(signedMessage["v"], 16), int(signedMessage["r"], 16), int(signedMessage["s"], 16)))

    recovered_address = Account.recover_message(
        encode_defunct(text=code_smell.auth_message),
        vrs=[int(i, 16) for i in signedMessage.values()])

    if recovered_address != address or code_smell.requested_auth != 1:
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
