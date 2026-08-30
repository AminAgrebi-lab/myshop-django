from .cart import Cart


def cart(request):
    """
    Context processor to make the current cart available in all templates.
    """
    # Return a dictionary containing the Cart instance
    return {'cart': Cart(request)}
