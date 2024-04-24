from django.db.models.signals import post_save
from django.dispatch import receiver
from products.models import Product
from products.services.product_services import invalidate_product_details_cache


@receiver(post_save, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Функция-получатель сигнала для сброса кэша при сохранении экземпляра Product.
    """
    product_id = instance.id
    invalidate_product_details_cache(product_id)
