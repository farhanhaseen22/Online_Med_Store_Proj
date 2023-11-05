from django.shortcuts import render
from .models import Product, OrderItem, ShippingAddress, FullOrder, Purchased_item, ProductCategories, Favored_Item
from .forms import ShippingForm , ShippingUpdateForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse , HttpResponseRedirect ,Http404
from django.urls import reverse
import datetime


# Create the views here...

##### Common Functions #####

def getting_cart_total(request):
    total_item_cart = 0
    items = OrderItem.objects.filter(user=request.user)
    for item in items:
        total_item_cart += item.quantity
    
    return total_item_cart;
        
def getting_cart_total_and_cost(items):
    total_cost_cart = 0
    total_item_cart = 0

    for item in items:
        total_item_cart += item.quantity

    for item in items:
        total_cost_cart += item.get_total

    return [total_item_cart,total_cost_cart];

####################

def store(request):

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories' : product_categories,
        'total_item_cart' : total_item_cart,
    }
    return render(request, 'store/store.html', context)



def checkout(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    items = []
    total_cost_cart = 0
    total_item_cart = 0

    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user = request.user)
        bulk = getting_cart_total_and_cost(items)
        total_item_cart = bulk[0]
        total_cost_cart = bulk[1]

    if total_item_cart == 0:
        return Http404

    form = ShippingForm()
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            adr = form.save(commit=False)
            adr.user = request.user
            adr.save()
        return HttpResponseRedirect(reverse('checkout'))

    addresses = ShippingAddress.objects.filter(user = request.user)

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories' : product_categories,
        'items': items,
        'total_item_cart': total_item_cart,
        'total_cost_cart': total_cost_cart,
        'form' : form,
        'addresses' : addresses,
    }
    return render(request, 'store/checkout.html', context)



@csrf_exempt
def insert_into_cart(request):

    total_item_cart = 0
    about = 'item_not_added'
    if request.user.is_authenticated:
        about = 'Item Added'
        product_id = request.POST.get('product_id')
        item_quantity = request.POST.get('item_quantity')

        product = Product.objects.get(id = product_id)
        
        if item_quantity == "0" or item_quantity == "":
            item_quantity = 1;
        else:
            item_quantity = int(item_quantity)
            if item_quantity < 1 or item_quantity > 9:
                item_quantity = 1;
        
        # print(type(product_id))
        # print(item_quantity)

        if OrderItem.objects.filter(product=product,user = request.user).exists():
            item = OrderItem.objects.get(product=product,user = request.user)
            item.quantity =  item.quantity + item_quantity
            item.save()
        else:
            item = OrderItem.objects.create(product = product,
                                            user = request.user,
                                            quantity = item_quantity)
            item.save()

        total_item_cart = getting_cart_total(request)


    dic = {
        'data' : about,
        'total_item_cart' : total_item_cart,
    }
    return JsonResponse(dic, safe=False)



@csrf_exempt
def update_item_quantity(request):
    about = 'Some Error Occurred'
    if request.user.is_authenticated:
        about = 'Item Updated'
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = Product.objects.get(id=product_id)
        item = OrderItem.objects.get(product=product, user=request.user)

        if action == 'add':
            item.quantity+=1
        else:
            item.quantity-=1
        item.save()

        if item.quantity <= 0 :
            item.delete()

    dic = {
        'data': about,
    }
    return JsonResponse(dic, safe=False)



def cart(request):

    items = []
    total_cost_cart=0
    total_item_cart=0

    if request.user.is_authenticated:
        items = OrderItem.objects.filter(user = request.user)
        bulk = getting_cart_total_and_cost(items)
        total_item_cart = bulk[0]
        total_cost_cart = bulk[1]

    if total_item_cart==0:
        check = False
    else:
        check = True

    product_categories = ProductCategories.objects.all()

    context = {
        'items' : items ,
        'total_item_cart' : total_item_cart,
        'total_cost_cart' : total_cost_cart,
        'check':check,
        'product_categories': product_categories,
    }
    return render(request, 'store/cart.html', context)



def item_detail(request,id):

    total_item_cart = 0

    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    Favored_Item_exists = False
    product = Product.objects.get(id=id)

    if Favored_Item.objects.filter(product = product, user = request.user).exists():
        Favored_Item_exists = True

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'product' : product,
        'total_item_cart' : total_item_cart,
        'Favored_Item_exists' : Favored_Item_exists,
    }

    return render(request,'store/item_detail.html',context)



def order_details(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    orders = FullOrder.objects.filter(user=request.user).order_by('-date_ordered')

    ordered = []
    for order in orders:
        tt = []
        items = Purchased_item.objects.filter(order=order)
        for item in items:
            tt.append(item)
        ordered.append({'order': order, 'items': tt})

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'ordered': ordered,
        'total_item_cart': total_item_cart,
    }

    return render(request,'store/order_details.html',context)


def fav_orders(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    fav_objects = Favored_Item.objects.filter(user=request.user)
    
    products_temp = []
    for object in fav_objects:
        product = Product.objects.filter(id=object.product_id)
        products_temp.append(product[0])

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'products': products_temp,
        'total_item_cart': total_item_cart,
    }

    return render(request,'store/fav_orders.html',context)


@csrf_exempt
def add_to_favs(request):

    total_item_cart = 0
    about = 'item_not_added'
    if request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id = product_id)
        if Favored_Item.objects.filter(product = product, user = request.user).exists():
            # about = 'You have already added this item to Favourites'
            about = 'Removed this item from Favourites'
            item = Favored_Item.objects.get(product=product, user=request.user)
            item.delete()
        else:
            item = Favored_Item.objects.create(product = product, user = request.user)
            item.save()
            about = 'Added to Favourites'

        total_item_cart = getting_cart_total(request)

    context = {
        'message' : about,
        'total_item_cart' : total_item_cart,
    }
    
    return JsonResponse(context, safe=False)
    # print(order)
    # return HttpResponse('')


def make_payment(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    dt = datetime.datetime.now()
    seq = int(dt.strftime("%Y%m%d%H%M%S"))

    adr = ShippingAddress.objects.get(id = id)
    obj = FullOrder.objects.create(user = request.user)

    obj.recepient_fullname = adr.recepient_fullname
    obj.phone_no = adr.phone_no
    obj.address_line1 = adr.address_line1
    obj.address_line2 = adr.address_line2
    obj.city = adr.city
    obj.state = adr.state
    obj.country = adr.country
    obj.zipcode = adr.zipcode
    obj.transaction_id = seq
    obj.save()

    total_amount = 0

    items = OrderItem.objects.all()
    for item in items:
        item_purchased = Purchased_item.objects.create(order = obj)
        item_purchased.user = request.user
        item_purchased.quantity = item.quantity
        item_purchased.name = item.product.name
        item_purchased.price = item.product.price
        item_purchased.image = item.product.image
        item_purchased.description = item.product.description
        item_purchased.save()
        total_amount += item.product.price * item.quantity

        item.delete()

    obj.amount = total_amount
    obj.save()

    return render(request,'store/payment_success.html')



def delete_address(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    adr = ShippingAddress.objects.get(id=id)

    if adr.user != request.user:
        return Http404

    adr.delete()
    return HttpResponseRedirect(reverse('checkout'))



def show_items(request,id):

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_category = ProductCategories.objects.get(id=id)
    products = Product.objects.filter(category=product_category)

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories' : product_categories,
        'product_category' : product_category,
        'products': products,
        'total_item_cart': total_item_cart,
    }
    return render(request, 'store/show_items.html', context)



def search(request):

    query = request.GET['search']

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()
    products_temp = Product.objects.all()

    products =[]

    for p in products_temp:
        if query.lower() in p.name.lower() or query.lower() in p.description.lower():
            products.append(p)

    context = {
        'products' : products,
        'product_categories': product_categories,
        'total_item_cart': total_item_cart,
    }

    return render(request, 'store/search.html', context)



def update_address(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()

    adr = ShippingAddress.objects.get(id=id)

    if adr.user != request.user:
        return Http404()

    if request.method == 'POST':
        form = ShippingUpdateForm(request.POST,instance=adr)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('checkout'))
    else:
        form = ShippingUpdateForm(instance=adr)

    context = {
        'product_categories' : product_categories,
        'total_item_cart' : total_item_cart,
        'form' : form ,
    }

    return render(request ,'store/update_address.html',context)