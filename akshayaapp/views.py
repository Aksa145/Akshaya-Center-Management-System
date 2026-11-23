# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from django.http import JsonResponse, HttpResponse
from django.db.models import Sum

from .models import Product, Sale,SaleItem

from openpyxl import Workbook
import json
import csv
from datetime import date
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from decimal import Decimal

from django.utils.timezone import localdate
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Bill, BillItem
from django.forms.models import model_to_dict



def login_view(request):

    message = ""

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)
            return redirect('dashboard')

        else:
            message = "Invalid Username or Password"

    return render(
        request,
        'login.html',
        {'message': message}
    )

# 

@login_required
def dashboard(request):

    # ✅ OWNER CAN SEE ALL DATA
    if request.user.is_superuser:
        sales = Sale.objects.all()
    else:
        # ✅ STAFF ONLY THEIR DATA
        sales = Sale.objects.filter(staff=request.user)

    # total_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # total_bills = sales.count()
    today = now().date()

# CURRENT MONTH SALES
    current_month_sales = sales.filter(
        sale_date__year=today.year,
        sale_date__month=today.month
    )


    total_sales = current_month_sales.aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0


    total_bills = current_month_sales.count()

    today_sales = sales.filter(
            sale_date=now().date()
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    total_staff = User.objects.count()

    recent_sales = sales.order_by('-id')[:10]

    return render(request, 'dashboard.html', {
        'total_sales': total_sales,
        'total_bills': total_bills,
        'today_sales': today_sales,
        'total_staff': total_staff,
        'recent_bills': recent_sales,
    })



def products(request):

    if request.method == "POST":

        name = request.POST['name']
        rate = request.POST['rate']

        Product.objects.create(
            name=name,
            rate=rate
        )

    products = Product.objects.all()

    return render(
        request,
        'products.html',
        {'products':products}
    )






@login_required
def sales(request):

    # ✅ FIX: show all staff except superuser
    staffs = User.objects.exclude(is_superuser=True)

    # ✅ FIX: convert QuerySet → JSON safe list
    products_qs = Product.objects.all()

    products = [
        {
            "id": p.id,
            "name": p.name,
            "rate": float(p.rate)
        }
        for p in products_qs
    ]

    return render(request, "sales.html", {
        "staffs": staffs,
        "products": products,
        "today_date": localdate().isoformat()
    })
def export_excel(request):

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    ws.append(["Date", "Staff", "Total"])

    sales = Sale.objects.all()

    for s in sales:
        ws.append([
            s.sale_date,
            s.staff.username,
            s.total_amount
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=report.xlsx'

    wb.save(response)

    return response



@login_required
def users_page(request):

    # 🔥 ONLY ADMIN CAN ACCESS
    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        User.objects.create(
            username=username,
            password=make_password(password)
        )

    users = User.objects.all()

    return render(request, 'users.html', {'users': users})



@login_required
# def save_bill(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)

#             staff_id = data.get("staff_id")
#             staff = User.objects.get(id=staff_id)

#             sale = Sale.objects.create(
#                 staff=staff,
#                 total_amount=0
#             )

#             total = 0

#             for item in data.get("items", []):
#                 qty = Decimal(item["qty"])
#                 rate = Decimal(item["rate"])
#                 amount = qty * rate

#                 SaleItem.objects.create(
#                     sale=sale,
#                     product_id=item["product_id"],
#                     qty=qty,
#                     rate=rate,
#                     amount=amount
#                 )

#                 total += amount

#             sale.total_amount = total
#             sale.save()

#             return JsonResponse({
#                 "status": "success",
#                 "bill_id": sale.id,
#                 "total": float(total)
#             })

#         except Exception as e:
#             return JsonResponse({
#                 "status": "error",
#                 "message": str(e)
#             })

def save_bill(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)

            items = data.get("items", [])

            if not items:
                return JsonResponse({
                    "status":"error",
                    "message":"No products selected"
                })

            staff_id = data.get("staff_id")

            if not staff_id:
                return JsonResponse({
                    "status":"error",
                    "message":"Staff required"
                })

            staff = User.objects.get(id=staff_id)

            sale = Sale.objects.create(
                staff=staff,
                total_amount=0
            )

            total = Decimal("0")

            for item in items:

                qty = Decimal(item["qty"])
                rate = Decimal(item["rate"])
                amount = qty * rate

                SaleItem.objects.create(
                    sale=sale,
                    product_id=item["product_id"],
                    qty=qty,
                    rate=rate,
                    amount=amount
                )

                total += amount


            sale.total_amount = total
            sale.save()


            return JsonResponse({
                "status":"success",
                "bill_id":sale.id,
                "total":float(total)
            })


        except Exception as e:

            return JsonResponse({
                "status":"error",
                "message":str(e)
            })



@login_required
def report_page(request):

    if request.user.is_superuser:
        sales = Sale.objects.all().order_by('-id')
    else:
        sales = Sale.objects.filter(staff=request.user).order_by('-id')

    staff = request.GET.get('staff')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if staff and staff != "All":
        sales = sales.filter(staff__username=staff)

    if from_date:
        sales = sales.filter(sale_date__gte=from_date)

    if to_date:
        sales = sales.filter(sale_date__lte=to_date)

    total = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # ✅ FINAL STRUCTURE: FLATTEN DATA (IMPORTANT)
    report_data = []

    for sale in sales:
        items = sale.items.all()

        for item in items:
            report_data.append({
                "id": sale.id,
                "date": sale.sale_date,
                "staff": sale.staff.username,
                "product": item.product.name,
                "amount": item.amount
            })

    return render(request, "reports.html", {
        "reports": report_data,
        "total": total
    })
# 



def export_csv(request):

    sales = Sale.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="akshaya_reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Staff', 'Date', 'Total'])

    for s in sales:
        writer.writerow([
            s.id,
            s.staff.username,
            s.sale_date,
            s.total_amount
        ])

    return response


# from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('login')


# EDIT SERVICE
def edit_product(request, pk):

    product = get_object_or_404(Product, id=pk)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.rate = request.POST.get("rate")
        product.save()
        return redirect("products")  # your service page name

    return render(request, "edit_product.html", {"product": product})


# DELETE SERVICE
def delete_product(request, pk):

    product = get_object_or_404(Product, id=pk)
    product.delete()

    return redirect("products")



@login_required
def change_password(request):

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keeps user logged in
            messages.success(request, "Password updated successfully")
            return redirect("dashboard")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "change_password.html", {"form": form})


from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    # your existing code
    return render(request, 'users.html')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def user_list(request):
    return render(request, 'users.html')

@login_required
def delete_user(request, user_id):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")

    user = get_object_or_404(User, id=user_id)

    # ❌ Prevent deleting another admin
    if user.is_superuser:
        return HttpResponseForbidden("Cannot delete admin")

    user.delete()
    return redirect('user_list')

def print_receipt(request, bill_id):
    sale = get_object_or_404(Sale, id=bill_id)
    return render(request, "receipt.html", {"sale": sale})

def edit_bill(request, bill_id):
    sale = get_object_or_404(Sale, id=bill_id)

    if request.method == "POST":
        total = 0

        # for item in sale.saleitem_set.all():
        for item in sale.items.all():
            qty = float(request.POST.get(f"qty_{item.id}", item.qty))
            rate = float(request.POST.get(f"rate_{item.id}", item.rate))

            amount = qty * rate

            item.qty = qty
            item.rate = rate
            item.amount = amount
            item.save()

            total += amount

        sale.total_amount = total
        sale.save()

        return redirect("dashboard")

    return render(request, "edit_sales.html", {
        "sale": sale
    })

@login_required
def delete_bill(request, bill_id):

    if not request.user.is_superuser:
        return HttpResponseForbidden("Not allowed")

    sale = get_object_or_404(Sale, id=bill_id)

    sale.delete()

    return redirect("dashboard")