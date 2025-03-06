from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order, OrderItem
from .forms import ProductForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.


def main(request):
    return render(request, 'store/main.html')


def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def _get_cart(request):
    """
    Utility function to get cart data from session.
    Cart is stored as a dictionary: { product_id (str): quantity }
    """
    return request.session.get('cart', {})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, "Product created successfully!")
            return redirect('product_detail', pk=product.pk)
        else:
            messages.error(request, "Product creation failed. Please correct the errors.")
    else:
        form = ProductForm()
    return render(request, 'store/product_create.html', {'form': form})


@login_required
def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = _get_cart(request)
    # Increment quantity (starting at 0 if not already present)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    _save_cart(request, cart)
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart_view')

def cart_view(request):
    cart = _get_cart(request)
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = Decimal('0.00')
    for product in products:
        quantity = cart.get(str(product.id))
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.info(request, "Your cart is empty!")
        return redirect('product_list')
    
    # GET: show order summary; POST: process checkout
    if request.method == 'GET':
        products = Product.objects.filter(id__in=cart.keys())
        cart_items = []
        total = Decimal('0.00')
        for product in products:
            quantity = cart.get(str(product.id))
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        context = {'cart_items': cart_items, 'total': total}
        return render(request, 'store/checkout.html', context)
    elif request.method == 'POST':
        # Dummy payment integration: simply create an order
        products = Product.objects.filter(id__in=cart.keys())
        total = Decimal('0.00')
        order = Order.objects.create(user=request.user)
        for product in products:
            quantity = cart.get(str(product.id))
            subtotal = product.price * quantity
            total += subtotal
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
        order.total = total
        order.status = 'C'  # Simulate completed payment
        order.save()
        # Clear the shopping cart
        request.session['cart'] = {}
        messages.success(request, "Order placed successfully!")
        return redirect('order_tracking')

@login_required
def order_tracking(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_tracking.html', {'orders': orders})
