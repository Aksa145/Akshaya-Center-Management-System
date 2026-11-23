from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_view, name='login'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('products/', views.products, name='products'),

    path('sales/', views.sales, name='sales'),

    # path('reports/', views.reports, name='reports'),

    path('export-excel/', views.export_excel, name='export_excel'),
    path('users/', views.users_page, name='users'),
    path('save-bill/', views.save_bill, name='save_bill'),
    path('reports/', views.report_page, name='reports'),
    # path('reports/', views.report_page, name='reports'),
    path('export/', views.export_csv, name='export'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('change-password/', views.change_password, name='change_password'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path("receipt/<int:bill_id>/", views.print_receipt, name="print_receipt"),
    path("edit-bill/<int:bill_id>/", views.edit_bill, name="edit_bill"),
    path(
    'delete-bill/<int:bill_id>/',
    views.delete_bill,
    name='delete_bill'
),


]