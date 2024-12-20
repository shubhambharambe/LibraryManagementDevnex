
from django.urls import path
from . import views
from api.views import (
    AuthorListCreateView, 
    AuthorDetailView, 
    BookListCreateView, 
    BookDetailView, 
    BorrowViewSet, 
    BorrowReturnView, 
    CategoryListCreate,
    CategoryRetrieveUpdateDestroy,
    GenerateReportView, 
    GetLatestReportView,
    ApproveBorrowRecordView
)
from rest_framework.routers import DefaultRouter
from .views import BorrowViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'borrow', BorrowViewSet, basename='borrow')


urlpatterns = [
    
    # Author URLs
    path('authors/', AuthorListCreateView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('categories/', CategoryListCreate.as_view(), name='book-categories'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='book-categoriesCRUD'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('borrow/<int:pk>/return/', BorrowReturnView.as_view(), name='borrow-return'),
    path('', include(router.urls)),
    path('reports/', GenerateReportView.as_view(), name='generate_report'),
    path('reports/latest/', GetLatestReportView.as_view(), name='get_latest_report'),
    path('borrow-records/<int:pk>/approve/', ApproveBorrowRecordView.as_view(), name='approve-borrow-record'),
]