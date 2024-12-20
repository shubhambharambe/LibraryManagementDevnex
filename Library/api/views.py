from rest_framework import generics, status
from .models import Category
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.conf import settings
from celery import shared_task
from .models import User, Author, Category, Book, BorrowRecord
from .serializers import BorrowRecordApprovalSerializer, UserSerializer, AuthorSerializer, CategorySerializer, BookSerializer, BorrowRecordSerializer
import os
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from .celery_task import generate_report
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from rest_framework import status, permissions
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import IsLibrarian,IsBorrowerOrlibrarian
from rest_framework.exceptions import PermissionDenied

# Author Views
class AuthorListCreateView(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    

# Book Views
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    

class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

# Borrow Record Views
class BorrowViewSet(CreateModelMixin, GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    

class BorrowReturnView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, pk, *args, **kwargs):
        try:
            borrow_record = BorrowRecord.objects.get(pk=pk)
            if borrow_record.return_date:
                return Response({"error": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

            borrow_record.return_date = now()
            borrow_record.book.available_copies += 1
            borrow_record.book.save()
            borrow_record.save()
            return Response(BorrowRecordSerializer(borrow_record).data, status=status.HTTP_200_OK)
        except BorrowRecord.DoesNotExist:
            return Response({"error": "Borrow record not found."}, status=status.HTTP_404_NOT_FOUND)
class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        task = generate_report.delay()  # Run report generation in the background
        return Response({'message': 'Report generation started.', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

class GetLatestReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        report_dir = os.path.join(os.getcwd(), 'reports')
        if not os.path.exists(report_dir):
            return Response({'message': 'No reports found.'}, status=status.HTTP_404_NOT_FOUND)

        reports = sorted(
            [f for f in os.listdir(report_dir) if f.startswith('report_')],
            reverse=True
        )
        if not reports:
            return Response({'message': 'No reports found.'}, status=status.HTTP_404_NOT_FOUND)

        latest_report = os.path.join(report_dir, reports[0])
        with open(latest_report, 'r') as f:
            report_data = json.load(f)

        return JsonResponse(report_data)
class ApproveBorrowRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            borrow_record = BorrowRecord.objects.get(pk=pk)
        except BorrowRecord.DoesNotExist:
            return Response({"error": "Borrow record not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.user_role != 'librarian':
            return Response({"error": "Only librarians can approve borrow requests."}, status=status.HTTP_403_FORBIDDEN)

        serializer = BorrowRecordApprovalSerializer(borrow_record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Borrow record updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
