import graphene
from graphene_django import DjangoObjectType

from sugomA.AmogusApp.models import Authentication


class AuthenticationType(DjangoObjectType):
    class Meta:
        model = Authentication
        fields = ("address", "isLandlord")


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
"""


class Query(graphene.ObjectType):
    authentication = graphene.Field(AuthenticationType)

    def resolve_authentication(root, info):
        return None


schema = graphene.Schema(query=Query)
