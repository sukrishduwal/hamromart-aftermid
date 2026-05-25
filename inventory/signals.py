from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InventoryLog

@receiver(post_save, sender=InventoryLog)
def update_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        # If action is Sale, quantity is negative. If Restock, positive.
        product.quantity += instance.change_quantity
        product.save()