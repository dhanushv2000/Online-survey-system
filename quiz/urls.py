from django.urls import path
from student import views
from django.urls import path,include
from django.contrib import admin
from quiz import views
from .views import admin_view_result_pdf_view

urlpatterns = [
path('admin_view_result_pdf_view/<int:pk>',admin_view_result_pdf_view.as_view(), name = 'admin-view-result-pdf'),

]
