from shops.models import Shop


def create_shop(user, data):
    """
    Создать магазин для указанного пользователя с предоставленными данными.
    """
    shop = Shop.objects.create(user=user, **data)
    return shop


def remove_shop(shop):
    """
    Удалить предоставленный магазин.
    """
    shop.delete()
