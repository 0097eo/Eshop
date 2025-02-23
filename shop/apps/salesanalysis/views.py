from django.shortcuts import render

from rest_framework import generics
from ..accounts.permissions import IsAdmin
from .models import SalesRecord
from .serializers import SalesRecordSerializer

from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SalesRecord

class SalesListView(generics.ListAPIView):
    permission_classes = [IsAdmin] 
    queryset = SalesRecord.objects.all()
    serializer_class = SalesRecordSerializer

class SalesReportView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        total_sales = SalesRecord.objects.aggregate(total=Sum("total_amount"))
        return Response({"total_sales": total_sales["total"]})

