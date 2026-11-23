from django.db import models

# Create your models here.
# from django.db import models
from django.contrib.auth.models import User

from decimal import Decimal




class Product(models.Model):
    name = models.CharField(max_length=200)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# class Sale(models.Model):
#     staff = models.ForeignKey(User, on_delete=models.CASCADE)
#     sale_date = models.DateField(auto_now_add=True)
#     total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     def __str__(self):
#         return f"{self.staff.username} - {self.sale_date}"
class Sale(models.Model):

    bill_no = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    sale_date = models.DateField(
        auto_now_add=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )


    def save(self, *args, **kwargs):

        if not self.bill_no:
            last_id = Sale.objects.count() + 1
            self.bill_no = f"AKS-{last_id:06d}"

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.bill_no} - {self.staff.username}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.amount = float(self.qty) * float(self.rate)
        super().save(*args, **kwargs)


# models.py

class Bill(models.Model):
    staff = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)