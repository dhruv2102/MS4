from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.db.models import Q
from .models import Product
from .forms import ProductForm

from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required

# Create your views here.


def all_products(request):
    """A view to handle all products, sorting and searching queries"""

    products = Product.objects.all()
    query = None
    sort = None
    direction = None

    # Add filtering by categories if necessary

    if request.GET:
        if "sort" in request.GET:
            sortkey = request.GET["sort"]
            sort = sortkey
            if sortkey == "name":
                sortkey = "lower_name"
                products = products.annotate(lower_name=Lower("name"))
            if sortkey == "category":
                sortkey = "category__name"
            if "direction" in request.GET:
                direction = request.GET["direction"]
                if direction == "desc":
                    sortkey = f"-{sortkey}"
            products = products.order_by(sortkey)

        if "q" in request.GET:
            query = request.GET["q"]
            if not query:
                messages.error(request, "You didn't enter any search criteria")
                return redirect(reverse("products"))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f"{sort}_{direction}"

    context = {
        "products": products,
        "search_term": query,
        "current_sorting": current_sorting,
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_id):
    """View to show product description"""

    product = get_object_or_404(Product, pk=product_id)
    context = {
        "product": product,
    }

    return render(request, "products/product_detail.html", context)

@login_required
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only super users can do that')
        return redirect(reverse('home'))

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, "Successfull add product!")
            return redirect(reverse("product_detail", args=[product.id]))
        else:
            messages.error(request, "Failed to add product. Please ensure for is valid")

    form = ProductForm()
    template = "products/add_product.html"
    context = {
        "form": form,
    }
    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only super users can do that')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully updated product!")
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure form is valid')
    form = ProductForm(instance=Product)
    messages.info(request, f'You are editing the product {product.name}')


    template = "products/edit_product.html"
    context = {
        "form": form,
        'product': product,
    }
    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only super users can do that')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
