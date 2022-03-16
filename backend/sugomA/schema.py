import secrets

from ariadne import (MutationType, ObjectType, QueryType, gql,
                     make_executable_schema)

from sugomA.AmogusApp.models import Authentication


code_smell = {}  # type: ignore


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

    return "super_" + secrets.token_urlsafe(30) + "_secret"


"""
Роли пользователей определяются следующим образом:
• Адрес аккаунта арендодателя передаётся приложению при запуске.
• Если в базе данных существует комната, арендованная пользователем,
  то он считается арендатором.
• Если в базе данных существует арендованная комната, в списке кассиров
  которой содержится адрес в сети блокчейн аккаунта пользователя,
  то этот пользователь — кассир.
• Аутентифицированный пользователь может не иметь роли, например, если он
  является потенциальным арендатором.
• Часть функций, например, получение квитанций, доступно и
  неаутентифицированным пользователям.
"""


@mutation.field("authenticate")
def resolve_authenticate(_, info, address, signedMessage):
    raise Exception("A")
    # if not code_smell.get("requested_auth", False):

    authentications = Authentication.objects.filter(address=address)

    if len(authentications) == 0:
        return Authentication.objects.create(
            address=address, isLandlord=False)

    return authentications[0]


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
