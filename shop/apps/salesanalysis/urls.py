from django.urls import path
from .views import SalesListView, SalesReportView

urlpatterns = [
    path("sales/", SalesListView.as_view(), name="sales-list"),
    path("sales/report/", SalesReportView.as_view(), name="sales-report"),
]
