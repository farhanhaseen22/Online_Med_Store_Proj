from django.urls import path
from . import views

urlpatterns = [
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('insert_cart/',views.insert_into_cart,name='insert_cart'),
    path('cart/update_item/',views.update_item_quantity,name='update_item'),

    path('item_detail/<int:id>',views.item_detail,name='item_detail'),
    path('order_details/',views.order_details,name='order_details'),
    path('fav_orders/',views.fav_orders,name='fav_orders'),
    path('add_to_favs/',views.add_to_favs,name='add_to_favs'),
    path('update_rating/',views.update_rating,name='update_rating'),

    path('make_payment/<int:id>',views.make_payment,name='make_payment'),
    path('delete_address/<int:id>', views.delete_address, name='delete_address'),
    path('update_address/<int:id>',views.update_address,name='update_address'),

    path('show_items/<int:id>',views.show_items,name='show_items'),
    path('search/',views.search,name='search'),

    path('recommendation_system/',views.recom_page,name='recom_page'),
    path('selection_for_recom/',views.selection_for_recom,name='selection_for_recom'),
]