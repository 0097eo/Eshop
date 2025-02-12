from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_pk>/reviews/', views.ProductReviewListCreateView.as_view(), name='product-review-list'),
    path('products/<int:product_pk>/reviews/<int:review_pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    path('wishlist/', views.WishListView.as_view(), name='wishlist'),
    path('wishlist/<int:product_id>/', views.WishListItemView.as_view(), name='wishlist-item'),
]