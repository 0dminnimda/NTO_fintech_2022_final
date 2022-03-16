from django.db import models


class Authentication(models.Model):
    address = models.TextField("address", default="")
    # address = models.CharField("address", max_length=128)
    isLandlord = models.BooleanField("isLandlord")

    def __str__(self):
        return (
            type(self).__name__ + "(" + str(self.address)
            + ", " + str(self.isLandlord) + ")")
