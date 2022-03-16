from ariadne import QueryType, make_executable_schema, gql, MutationType, ObjectType

type_defs = gql("""
type Query {
    authentication: Authentication
}

type Mutation {
    requestAuthentication(address: String!): String!
    authenticate(
        address: String!
        signedMessage: InputSignature!
    ): Authentication!
}

type Authentication {
    address: String!
    isLandlord: Boolean!
}

input InputSignature {
    v: String!
    r: String!
    s: String!
}
""")

"""
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
mutation = MutationType()


@query.field("authentication")
def resolve_authentication(root, info):
    print(root, info)
    return info["authentication"]


authentication = ObjectType("Authentication")


@authentication.field("address")
def resolve_address(root, info):
    return "gg"


@authentication.field("isLandlord")
def resolve_isLandlord(root, info):
    return False


schema = make_executable_schema(
    type_defs, [query, mutation], authentication)  # type: ignore
