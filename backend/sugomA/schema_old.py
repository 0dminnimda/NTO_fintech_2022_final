import graphene
from graphene_django import DjangoObjectType

from sugomA.AmogusApp.models import Authentication


class AuthenticationType(DjangoObjectType):
    class Meta:
        model = Authentication
        fields = ("address", "isLandlord")


"""
type Query {
    authentication: Authentication
}

type Mutation {
    requestAuthentication(address: String!): String!
    authenticate(
        address: String!
        signedMessage: {v, r, s}
    ): Authentication!
}

type Authentication {
    address: String!
    isLandlord: Boolean!
}

# input InputSignature {
#     v: String!
#     r: String!
#     s: String!
# }
"""

"""
query {
    authentication { address, isLandlord }
}
->
{
    "data": {
        "authentication": null
    }
}

mutation {
    message: requestAuthentication(
        address: "<address-0>"
    )
}
->
{
    "data": {
        "message": "<message-0>"
    }
}

"""


# class RequestAuthentication(graphene.Mutation):
#     class Arguments:
#         address = graphene.String(required=True)

#     gg = graphene.String(required=False)

#     def mutate(root, info, address):
#         print(root, info)
#         Authentication.objects.create(address=address, isLandlord=False)
#         return RequestAuthentication("freak-off")


# class RequestAuthentication():
#     address: String! String!

# class RequestAuthentication(graphene.ObjectType):
#     class Arguments:
#         address = graphene.String(required=True)


# class Mutation(graphene.ObjectType):
#     request_authentication = RequestAuthentication()
#     # request_authentication = graphene.Field(
#     #     graphene.String,
#     #     address=graphene.String)  #RequestAuthentication.Field()

#     def resolve_request_authentication(root, info, address):
#         return "suck_ma-balls"


"""

mutation {
    message: requestAuthentication(
        address: "<address-0>"
    )
}
->
{
    "data": {
        "message": "<message-0>"
    }
}

"""

"""
mutation {
    authentication: authenticate(
        address: "<address-0>"
        signedMessage: {
            signature: {
                v: "<v-0>",
                r: "<r-0>",
                s: "<s-0>"
            }
        }
    ) {
        address
        isLandlord
    }
}
->
{
    "data": {
        "authentication": {
            "address": "<address-0>",
            "isLandlord": false
        }
    }
}

"""


"""
5
query {
    authentication { address, isLandlord }
}
->
{
    "data": {
        "authentication": {
            "address": "<address-0>",
            "isLandlord": false
        }
    }
}

---

9
query {
    authentication { address, isLandlord }
}
->
{
    "data": {
        "authentication": {
            "address": "<landlord-address>",
            "isLandlord": true
        }
    }
}

"""


class Query(graphene.ObjectType):
    authentication = graphene.Field(AuthenticationType)

    def resolve_authentication(root, info):
        return None


schema = graphene.Schema(
    query=Query,
    # mutation=Mutation
)
