from django.shortcuts import get_object_or_404, render
from .models import Category, Product

# Import the form to handle adding products to the cart
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'categories': categories,
            'products': products
        }
    )


def product_detail(request, id, slug):
    """
    View to display a single product and provide a form to add it to the cart.
    """
    product = get_object_or_404(
        Product, id=id, slug=slug, available=True
    )

    # Initialize the form to be used in the product detail template
    cart_product_form = CartAddProductForm()

    return render(
        request,
        'shop/product/detail.html',
        {
            'product': product,
            'cart_product_form': cart_product_form  # Pass the form to the template
        }
    )
