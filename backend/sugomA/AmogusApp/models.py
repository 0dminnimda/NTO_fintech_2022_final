import uuid

from django.db import models


class Authentication(models.Model):
    address = models.TextField("address", default="")
    isLandlord = models.BooleanField("isLandlord")

    def __str__(self):
        return (
            type(self).__name__ + "(" + str(self.address)
            + ", " + str(self.isLandlord) + ")")


class Room(models.Model):
    id = models.UUIDField("id", primary_key=True, default=uuid.uuid4, editable=False)
    internalName = models.TextField("internalName", default="")
    area = models.FloatField("area")
    location = models.TextField("location", default="")

    contractAddress = models.TextField("contractAddress", null=True)
    publicName = models.TextField("publicName", null=True)
