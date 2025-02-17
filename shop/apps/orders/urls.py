from . import views
from django.urls import path

urlpatterns = [
    path('orders/', views.OrderListCreateView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateFromCartView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('orders/<int:pk>/address/', views.OrderAddressUpdateView.as_view(), name='order-address-update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order-delete'),
]