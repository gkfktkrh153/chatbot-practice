from django.db import models


class Fruits(models.Model):
    name = models.CharField(max_length=50)
    descript = models.TextField()
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return 'id : {},name : {},description : {}'.format(self.id, self.name, self.descript)