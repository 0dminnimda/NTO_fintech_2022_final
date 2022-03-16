import secrets
from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)

from sugomA.AmogusApp.models import Authentication
import time
import eth_keys
import sqlite3


code_smell = {}  # type: ignore

con = sqlite3.connect('sqlite.db', check_same_thread=False)
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Messages
               (address text, message text)''')
con.commit()


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
    return None


mutation = MutationType()


@mutation.field("requestAuthentication")
def resolve_request_authentication(_, info, address):
    code_smell["requested_auth"] = True

    message = f'{int(time.time())}_{secrets.token_urlsafe(30)}'

    cur.execute(f'INSERT INTO Messages VALUES ("{address}", "{message}")')
    con.commit()

    return message


@mutation.field("authenticate")
def resolve_authenticate(_, info, address, signedMessage):
    authentications = Authentication.objects.filter(address=address)

    if len(authentications) == 0:
        return Authentication.objects.create(
            address=address, isLandlord=False)

    cur.execute('SELECT message FROM Messages WHERE address = "{address}"')
    message = cur.fetchone()[0]
    signature = eth_keys.KeyAPI.Signature(vrs=(signedMessage.v, signedMessage.r, signedMessage.s,))
    signer = signature.recover_public_key_from_msg(message)

    if signer == address:
        return authentications[0]
    raise Exception("Authentication failed")


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
