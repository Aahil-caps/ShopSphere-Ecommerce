from django.shortcuts import render, redirect
from .models import Products, Order
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateAPIView,DestroyAPIView,RetrieveAPIView,CreateAPIView,UpdateAPIView
from .serializer import SerializerProduct
from rest_framework.views import APIView
from rest_framework.response import Response

def product_list(request):
    name = request.GET.get('name')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    max_stock = request.GET.get('max_stock')
    min_stock = request.GET.get('min_stock')
    sort = request.GET.get('sort')

    product = Products.objects.all()

    if min_stock:
        product = product.filter(stock__gte=min_stock)

    if max_stock:
        product = product.filter(stock__lte=max_stock)

    if name:
        product = product.filter(name__icontains=name)

    if sort == "name_asc":
        product = product.order_by("name")

    if sort == "name_desc":
        product = product.order_by("-name")

    if min_price:
        product = product.filter(price__gte=min_price)

    if max_price:
        product = product.filter(price__lte=max_price)

    if sort == 'asc':
        product = product.order_by('price')

    if sort == 'desc':
        product = product.order_by("-price")

    paginator = Paginator(product, 2)
    page = request.GET.get('page')
    product = paginator.get_page(page)

    return render(request, 'product_list.html', {"product": product})


def product_detail(request, pk):
    product = Products.objects.get(id=pk)
    return render(request, 'product_detail.html', {"product": product})


def add_to_cart(request, pk):
    product = Products.objects.get(id=pk)

    if product.stock <= 0:
        return redirect('product_detail', pk=pk)

    cart = request.session.get('cart', {})

    if str(pk) in cart:
        if cart[str(pk)] < product.stock:
            cart[str(pk)] += 1
        else:
            messages.error(request, "Maximum stock reached")
    else:
        cart[str(pk)] = 1

    request.session['cart'] = cart

    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', {})

    product_ids = Products.objects.values_list('id', flat=True)

    for id in list(cart.keys()):
        if int(id) not in product_ids:
            del cart[id]

    request.session['cart'] = cart

    product = Products.objects.filter(id__in=cart.keys())

    grand_total = 0

    for p in product:
        quantity = cart[str(p.id)]
        p.quantity = quantity

        total = p.price * quantity
        p.total = total
        grand_total += total

    return render(request, 'cart.html', {
        "product": product,
        "cart": cart,
        "grand_total": grand_total
    })


def remove_cart(request, pk):
    cart = request.session.get('cart', {})

    pk = str(pk)

    if pk in cart:
        del cart[pk]

    request.session['cart'] = cart

    if not cart:
        messages.error(request, "Your cart is empty")

    return redirect('cart')


def increase_cart(request, pk):
    cart = request.session.get('cart', {})
    product = Products.objects.get(id=pk)

    pk = str(pk)

    if pk in cart:
        if cart[pk] < product.stock:
            cart[pk] += 1
        else:
            messages.success(request, "Maximum stock reached")

    request.session['cart'] = cart

    return redirect('cart')


def decrease_cart(request, pk):
    cart = request.session.get('cart', {})

    pk = str(pk)

    if pk in cart:
        cart[pk] -= 1

        if cart[pk] <= 0:
            del cart[pk]

    request.session['cart'] = cart

    return redirect('cart')


def checkout(request):
    cart = request.session.get('cart', {})
    grand_total = 0

    product = Products.objects.filter(id__in=cart.keys())

    for p in product:
        quantity = cart[str(p.id)]
        p.quantity = quantity

        total = p.price * quantity
        p.total = total

        grand_total += total

    return render(request, 'checkout.html', {
        "product": product,
        "grand_total": grand_total
    })


@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Cart is empty")
        return redirect('checkout')

    for p in cart:
        product = Products.objects.get(id=p)
        quantity = cart[p]

        if product.stock < quantity:
            messages.error(request, "Error Message")
            return redirect('checkout')

    for p in cart:
        product = Products.objects.get(id=p)
        quantity = cart[p]

        product.stock -= quantity
        product.save()

        total = product.price * quantity

        Order.objects.create(
            product=product,
            quantity=quantity,
            total=total,
            user=request.user,
            status="Confirmed"
        )

    request.session['cart'] = {}

    messages.success(request, "Order placed successfully!")

    return redirect('order_success')


def order_success(request):
    return render(request, 'order.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match")

        else:
            User.objects.create_user(
                username=username,
                password=password
            )

            messages.success(request, "Registration successful!")

            return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            username=username,
            password=password
        )

        if user:
            login(request, user)
            messages.success(request, "Login Successful")

            return redirect('product_list')

        else:
            messages.error(request, "Passwords do not match")

            return render(request, 'login.html')

    return render(request, 'login.html')


@login_required
def my_orders(request):
    status = request.GET.get('status')
    name = request.GET.get('name')

    orders = Order.objects.filter(user=request.user)

    if status:
        orders = orders.filter(status=status)

    if name:
        orders = orders.filter(
            product__name__icontains=name
        )

    paginator = Paginator(orders, 5)
    page = request.GET.get("page")
    orders = paginator.get_page(page)

    return render(
        request,
        "my_order.html",
        {
            "orders": orders,
            "status": status,
            "name": name,
        }
    )


@login_required
def cancel_order(request, pk):
    order = Order.objects.get(
        user=request.user,
        id=pk
    )

    if order.status == "Delivered":
        messages.error(request, "cannot cancel the order")
        return redirect("my_orders")

    if order.status == "Cancelled":
        return redirect("my_orders")

    if request.method == "POST":
        order.status = "Cancelled"

        product = order.product
        product.stock += order.quantity
        product.save()

        order.save()

        return redirect("my_orders")

    return redirect("my_orders")


def order_detail(request, pk):
    order = Order.objects.get(
        user=request.user,
        id=pk
    )

    return render(
        request,
        'order_detail.html',
        {"order": order}
    )


def clear_cart(request):
    request.session['cart'] = {}

    messages.success(request, "Cart cleared")

    return redirect('cart')


class update(ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = SerializerProduct


class modify(RetrieveUpdateAPIView):
    queryset = Products.objects.all()
    serializer_class = SerializerProduct    


class de(DestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = SerializerProduct


class re(RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = SerializerProduct

class cr(CreateAPIView):
    queryset = Products.objects.all()
    serializer_class = SerializerProduct
    
class up(UpdateAPIView):
    queryset = Products.objects.all()
    serializer_class = SerializerProduct




class ProductCount(APIView):
    def get(self,request):
        total = Products.objects.count()
        return Response({"total_products": total
        })


class ProductStockAPIView(APIView):
    def get(self,request):
        product = Products.objects.all()
        serializer = SerializerProduct(product,many=True)
        return Response(serializer.data)



class p(APIView):
    def get(self,request,pk):
        product = Products.objects.get(id=pk)
        serializer = SerializerProduct(product)
        return Response(serializer.data)

class pt(APIView):
    def put(self,request,pk):
        product = Products.objects.get(id=pk)
        serializer = SerializerProduct(product,data=request.data)

        if serializer.is_valid():
         serializer.save()
         return Response(serializer.data)
        else:
            return Response(serializer.errors)


class d(APIView):
    def post(self,request):
        serializer = SerializerProduct(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class e(APIView):
    def get(self,request,pk):
        product = Products.objects.get(id=pk)
       
        if product.stock > 0:
            in_stock = True
        else:
            in_stock = False


        return Response({"in_stock": in_stock})


class ProductAvailabilityAPIView(APIView):
    def get(self,request,pk):
        product = Products.objects.get(id=pk)
        if product.stock > 0:
            revert = "Available"
        else:
            revert = "Out of Stock"

        return Response({"revert":revert})