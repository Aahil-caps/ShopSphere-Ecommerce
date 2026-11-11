from django.db import models
from django.contrib.auth.models import User

class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    stock = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)



    def __str__(self):
        return self.name

class Order(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.BigIntegerField()
    created_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    status = models.CharField(max_length=20,choices=[
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ],
    default="Pending"
    )


    def __str__(self):
        return str(self.product)