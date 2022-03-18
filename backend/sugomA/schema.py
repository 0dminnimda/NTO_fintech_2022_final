import json
import os
import secrets
import uuid
from copy import copy
from pathlib import Path
from time import time

from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_keys.exceptions import BadSignature, ValidationError
from web3 import Web3
from web3.exceptions import InvalidAddress

from sugomA.AmogusApp.models import Authentication, Room

from .exceptions import (AuthenticationFailed, ContractNotFound,
                         InvalidRoomParams, NotLandlordAccess,
                         RemovingRentedRoom, RoomNotFound, UnauthorizedAccess)

with open(Path(__file__).parent / "abi.txt") as f:
    ABI = json.loads(f.read())


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
        print("-"*5 + "reset" + "-"*5)
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
    print("authentication", code_smell["successfull_auth"],
          Authentication.objects.filter(address=code_smell["address"]),
          code_smell)

    if not code_smell["successfull_auth"]:
        return None

    return Authentication.objects.get(address=code_smell["address"])


# rooms: [Room!]!


def get_existing_room(id):
    try:
        uid = uuid.UUID(id)
    except ValueError as e:
        print("get_existing_room failure", e, id)
        raise RoomNotFound

    rooms = Room.objects.filter(id=uid)
    if len(rooms) == 0:
        print("get_existing_room failure", id, uid, rooms)
        raise RoomNotFound

    assert len(rooms) == 1
    return rooms[0]


@query.field("room")
def resolve_room(_, info, id):
    print("room", id)
    return get_existing_room(id)


mutation = MutationType()


@mutation.field("requestAuthentication")
def resolve_request_authentication(_, info, address):
    code_smell.reset()
    code_smell["requested_auth"] = 2

    message = str(time()) + "_" + secrets.token_urlsafe(30)
    print("requestAuthentication", address, message, code_smell)
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
    # session = info.context["request"].session

    try:
        recovered = Account.recover_message(
            encode_defunct(text=code_smell["auth_message"]),  # type: ignore
            vrs=[int(i, 16) for i in signedMessage.values()])
    except (BadSignature, ValidationError) as e:
        print("authenticate failure", e, address, signedMessage, code_smell)
        raise AuthenticationFailed

    print("authenticate", address, recovered, signedMessage, code_smell)
    if recovered.lower() != address.lower() or code_smell["requested_auth"] != 1:
        print("authenticate failure", recovered, address, code_smell["requested_auth"])  # noqa
        code_smell.reset()
        raise AuthenticationFailed

    code_smell["successfull_auth"] = True
    code_smell["address"] = address
    authentications = Authentication.objects.filter(address=address)

    if len(authentications) != 0:  # should be 1
        return authentications[0]

    isLandlord = os.environ.get("LANDLORD_ADDRESS", "<none>")
    print("isLandlord", address, isLandlord)
    return Authentication.objects.create(
        address=address, isLandlord=(address == isLandlord))


def require_authentication():
    if not code_smell["successfull_auth"]:
        print("require_authentication failure", code_smell["successfull_auth"], code_smell)  # noqa
        raise UnauthorizedAccess


def require_landlord(authentication):
    if not authentication.isLandlord:
        print("require_landlord failure", authentication.isLandlord, authentication)  # noqa
        raise NotLandlordAccess


def validate_room(room):
    if room["area"] <= 0:
        print("validate_room failure", room["area"], room)
        raise InvalidRoomParams


@mutation.field("createRoom")
def resolve_create_room(_, info, room):
    print("createRoom", room)

    require_authentication()
    require_landlord(Authentication.objects.get(address=code_smell["address"]))
    validate_room(room)

    # each room have unique id, so no worries about multiple instances
    return Room.objects.create(internalName=room["internalName"],
                               area=room["area"], location=room["location"])


@mutation.field("editRoom")
def resolve_edit_room(_, info, id, room):
    print("editRoom", id, room)

    require_authentication()
    require_landlord(Authentication.objects.get(address=code_smell["address"]))
    db_room = get_existing_room(id)
    validate_room(room)

    for name, value in room.items():
        setattr(db_room, name, value)

    db_room.save()
    return db_room


def check_contract_address(address):
    if address is None:
        return

    RPC_URL = os.environ.get("RPC_URL", None)
    assert RPC_URL is not None
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    try:
        code = w3.eth.get_code(address)
    except InvalidAddress as e:
        print("check_contract_address failure", e, address, RPC_URL, w3)
        raise ContractNotFound

    if code.hex() == "0x":
        print("check_contract_address failure", code.hex())
        raise ContractNotFound


@mutation.field("setRoomContractAddress")
def resolve_set_room_contract_address(_, info, id, contractAddress=None):
    print("setRoomContractAddress", id, contractAddress)

    require_authentication()
    require_landlord(Authentication.objects.get(address=code_smell["address"]))
    room = get_existing_room(id)
    check_contract_address(contractAddress)

    room.contractAddress = contractAddress
    room.save()

    return room


# setRoomPublicName(id: ID!, publicName: String): Room!


def is_room_rented(room):
    RPC_URL = os.environ.get("RPC_URL", None)
    assert RPC_URL is not None
    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    counter = w3.eth.contract(address=room.contractAddress, abi=ABI)
    rent_end_time = counter.functions.getRentEndTime().call()
    if time() < rent_end_time:
        print("is_room_rented failure", time(), ">=", rent_end_time)
        raise RemovingRentedRoom


@mutation.field("removeRoom")
def resolve_remove_room(_, info, id):
    print("setRoomContractAddress", id)

    require_authentication()
    require_landlord(Authentication.objects.get(address=code_smell["address"]))

    room = get_existing_room(id)
    is_room_rented(room)

    room_copy = copy(room)
    room.delete()
    return room_copy


schema = make_executable_schema(
    gql(type_defs), query, mutation,
    # authentication
)  # type: ignore
