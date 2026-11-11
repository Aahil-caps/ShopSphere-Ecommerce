from django.urls import path
from .import views
from .views import update,modify,de,re,cr,up,ProductCount,ProductStockAPIView

urlpatterns = [
    path('',views.product_list,name='product_list'),
    path('products/<int:pk>/',views.product_detail,name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('remove/<int:pk>/', views.remove_cart, name='remove_cart'),
    path('increase/<int:pk>/', views.increase_cart, name='increase_cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('decrease/<int:pk>/', views.decrease_cart, name='decrease_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
    path('order_success/', views.order_success, name='order_success'),
    path('logins/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login_view'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:pk>/', views.cancel_order, name='cancel_order'),
    path('order_detail/<int:pk>/', views.order_detail, name='order_detail'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('update/', update.as_view(), name='update'),
    path('modify/<int:pk>/', modify.as_view(), name='modify'),
    path('de/<int:pk>/', de.as_view(), name='de'),
    path('re/<int:pk>/', re.as_view(), name='re'),
    path('cr/', cr.as_view(), name='cr'),
    path('up/<int:pk>/', up.as_view(), name='up'),
    path('product-count/', ProductCount.as_view(), name='product_count'),
    path('jim/', ProductStockAPIView.as_view(), name='ProductStockAPIView')
]