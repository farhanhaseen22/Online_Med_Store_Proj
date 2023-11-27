# For the recommendation system
import numpy as np
import pandas as pd
import warnings
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

from django.shortcuts import render
from .models import Product, Cart_Item, Shipping_Addresse, Order_Addr_info, Purchased_Item, ProductCategories, Favored_Item, Item_Rating
from .forms import ShippingForm , ShippingUpdateForm
from django.db.models import Count, Sum

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse , HttpResponseRedirect ,Http404
from django.urls import reverse
import datetime


# Now, we create user-item matrix using scipy csr matrix
def create_matrix(df):
    
    N = len(df['user_id'].unique())
    M = len(df['product_id'].unique())

    # Map Ids to indices
    user_mapper = dict(zip(np.unique(df["user_id"]), list(range(N))))
    product_mapper = dict(zip(np.unique(df["product_id"]), list(range(M))))

    # Map indices to IDs
    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["user_id"])))
    product_inv_mapper = dict(zip(list(range(M)), np.unique(df["product_id"])))

    user_index = [user_mapper[i] for i in df['user_id']]
    product_index = [product_mapper[i] for i in df['product_id']]

    csr = csr_matrix((df["rating"], (product_index, user_index)), shape=(M, N))

    return csr, user_mapper, product_mapper, user_inv_mapper, product_inv_mapper


def find_similar_products(product_id, csr_mat, product_mapper, product_inv_mapper, k):
	
    neighbour_ids = []
    # print(f"ID:{product_id} and type:{type(product_id)}")
    # print(product_mapper)
    # print(product_inv_mapper)

    product_ind = product_mapper[int(product_id)]
    product_vec = csr_mat[product_ind]
    k+=1
    kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric='cosine')
    kNN.fit(csr_mat)
    product_vec = product_vec.reshape(1,-1)
    neighbour = kNN.kneighbors(product_vec, return_distance=False)
    for i in range(0,k):
        n = neighbour.item(i)
        neighbour_ids.append(product_inv_mapper[n])
    neighbour_ids.pop(0)
    return neighbour_ids


@csrf_exempt
def selection_for_recom(request):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    #################################################
    all_ratings = Item_Rating.objects.values('id', 'user_id', 'product_id', 'rating')
    all_ratings_df = pd.DataFrame(all_ratings)
    # all_products = Product.objects.values('id', 'name')
    # all_products_df = pd.DataFrame(all_products)

    ######## CSR ########
    csr_mat, user_mapper, product_mapper, user_inv_mapper, product_inv_mapper = create_matrix(all_ratings_df)
    ######## Find similar products ########
    gained_product_ids=[]
    # product_id = 1
    subcat_val = request.POST.get('subcat_val')
    
    similar_ids = find_similar_products(subcat_val, csr_mat, product_mapper, product_inv_mapper, k=6)

    for idx in similar_ids:
        gained_product_ids.append(idx)
    
    gained_products = Product.objects.filter(id__in=gained_product_ids)
    
    ######## final ########
    
    gained_products = list(gained_products.values())

    # print("\nCheck - 1\n")
    return JsonResponse(gained_products, safe=False)

def recom_page(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()
    products = Product.objects.values('id', 'name')
    # sub_categories_of_products = Product.objects.values('subcategory').distinct()

    context = {
        # 'sub_categories_of_products' : sub_categories_of_products,
        'products' : products,
        'product_categories' : product_categories,
        'total_item_cart' : total_item_cart
    }

    return render(request,'store/recommendation_system.html',context)


##### Common Functions #####

def getting_cart_total(request):
    total_item_cart = 0
    items = Cart_Item.objects.filter(user=request.user)
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

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories' : product_categories,
        'total_item_cart' : total_item_cart,
    }
    return render(request, 'store/store.html', context)



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

        if Cart_Item.objects.filter(product=product,user = request.user).exists():
            item = Cart_Item.objects.get(product=product,user = request.user)
            item.quantity =  item.quantity + item_quantity
            item.save()
        else:
            item = Cart_Item.objects.create(product = product,
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
        item = Cart_Item.objects.get(product=product, user=request.user)

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
        items = Cart_Item.objects.filter(user = request.user)
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
    if Item_Rating.objects.filter(product = product, user = request.user).exists():
        item = Item_Rating.objects.get(product = product, user = request.user)
    else:
        item = False

    if Favored_Item.objects.filter(product = product, user = request.user).exists():
        Favored_Item_exists = True

    product_categories = ProductCategories.objects.all()

    context = {
        'product_categories': product_categories,
        'product' : product,
        'item' : item,
        'total_item_cart' : total_item_cart,
        'Favored_Item_exists' : Favored_Item_exists,
    }

    return render(request,'store/item_detail.html',context)


# order history list
def order_details(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    orders = Order_Addr_info.objects.filter(user=request.user).order_by('-date_ordered')

    ordered = []
    for order in orders:
        tt = []
        items = Purchased_Item.objects.filter(order=order)
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

    context = {
        'message' : about
    }
    
    return JsonResponse(context, safe=False)


@csrf_exempt
def update_rating(request):

    if request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        selected_rating = request.POST.get('selected_rating')
        about = 0

        if int(selected_rating):
            num_sr = int(selected_rating)
            if 0 < num_sr < 6:
                product = Product.objects.get(id = product_id)

                if Item_Rating.objects.filter(product = product, user = request.user).exists():
                    item = Item_Rating.objects.get(product = product, user = request.user)
                    item.rating = selected_rating
                    item.save()
                else:
                    item = Item_Rating.objects.create(product = product, user = request.user, rating = selected_rating)
                    item.save()
                # whether new Item Rating is created or Item Rating is updated
                # Product is always needed to be updated
                calc_item_count = Item_Rating.objects.filter(product = product).count()
                calc_allratings = Item_Rating.objects.filter(product = product).aggregate(sum_amount=Sum('rating'))['sum_amount']
                calc_final_ratings = calc_allratings/(calc_item_count)
                
                print(f"Final rating: {calc_final_ratings}")
                product.rating = calc_final_ratings
                product.save()
                about = 1
        
    return JsonResponse(about, safe=False)



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



def make_payment(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    dt = datetime.datetime.now()
    seq = int(dt.strftime("%Y%m%d%H%M%S"))

    adr = Shipping_Addresse.objects.get(id = id)
    obj = Order_Addr_info.objects.create(user = request.user)

    # Order_Addr_info is for the address info order history list
    obj.name = adr.name
    obj.phone_number = adr.phone_number
    obj.shipping_address = adr.shipping_address
    obj.city = adr.city
    obj.state = adr.state
    obj.country = adr.country
    obj.zipcode = adr.zipcode
    obj.transaction_id = seq
    obj.save()

    total_amount = 0

    # Purchased_Item is for the product info order history list
    items = Cart_Item.objects.all()
    for item in items:
        item_purchased = Purchased_Item.objects.create(order = obj)
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


    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()

    context = {
        'transaction_id' : seq,
        'product_categories': product_categories,
        'total_item_cart': total_item_cart,
    }

    return render(request,'store/payment_success.html', context)



def checkout(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    items = []
    total_cost_cart = 0
    total_item_cart = 0

    if request.user.is_authenticated:
        items = Cart_Item.objects.filter(user = request.user)
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

    addresses = Shipping_Addresse.objects.filter(user = request.user)

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



def delete_address(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    adr = Shipping_Addresse.objects.get(id=id)

    if adr.user != request.user:
        return Http404

    adr.delete()
    return HttpResponseRedirect(reverse('checkout'))



def update_address(request,id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_login'))

    total_item_cart = 0
    if request.user.is_authenticated:
        total_item_cart = getting_cart_total(request)

    product_categories = ProductCategories.objects.all()

    adr = Shipping_Addresse.objects.get(id=id)

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
