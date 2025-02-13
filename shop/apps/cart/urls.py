from . import views
from django.urls import path


urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/item/<int:item_id>/', views.CartItemView.as_view(), name='cart-item'),
]