# from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from .forms import BookingForm,SignUpForm
from django.contrib.auth import login,authenticate,logout
from .models import Menu, Cart, Order, CartItem, OrderItem, Booking
from django.core import serializers
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm #add this
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def reservations(request):
    date = request.GET.get('date', datetime.today().date())
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html', {"bookings": booking_json})


def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservation successful. Our Representative will contact you to confirm your reservation." )
    context = {'form': form}
    return render(request, 'book.html', context)


def register_request(request):
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = SignUpForm()
	return render (request=request, template_name="signup.html", context={"register_form":form})


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("home")


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
        
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

# Add your code here to create new views
def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})


def display_menu_item(request, pk=None):
    if pk:
        menu_item = Menu.objects.get(pk=pk)
    else:
        menu_item = ""
    return render(request, 'menu_item.html', {"menu_item": menu_item})


def bookings(request):
    if request.method == 'POST':
        data = json.load(request)
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(
            reservation_slot=data['reservation_slot']).exists()
        if exist == False:
            booking = Booking(
                first_name=data['first_name'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot'],
            )
            booking.save()
        else:
            return HttpResponse("{'error':1}", content_type='application/json')

    date = request.GET.get('date', datetime.today().date())

    bookings = Booking.objects.all().filter(user=request.user)
    booking_json = serializers.serialize('json', bookings)

    return HttpResponse(booking_json, content_type='application/json')


def add_to_cart(request, menu_id):
    menu = Menu.objects.get(pk=menu_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, menu=menu)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('menu')


def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        total = 0
        for i in items:
             total+=i.menu.price*i.quantity

    except ObjectDoesNotExist:
        total = 0
        cart = None
    return render(request, 'cart.html', {'cart': cart, 'total': total})

def place_order(request):
    cart = Cart.objects.get(user=request.user)
    order = Order.objects.create(user=request.user)

    for cart_item in cart.cartitem_set.all():
        OrderItem.objects.create(order=order, menu=cart_item.menu, quantity=cart_item.quantity)

    cart.items.clear()
    return redirect('orders')

def orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order)
    total = 0
    for i in items:
        total+=i.menu.price*i.quantity
    return render(request, 'order.html', {'order': order,'total':total})


def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart')  # Redirect to the cart pag