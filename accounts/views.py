from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout

@login_required
def staff_management(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only admin can access staff management.")

    staff_list = User.objects.filter(groups__isnull=False).distinct()
    groups = Group.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        group_id = request.POST.get("group")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("staff_management")

        group = Group.objects.get(id=group_id)

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user.groups.add(group)

        messages.success(request, "Staff added successfully!")
        return redirect("staff_management")

    return render(request, "staff/staff_management.html", {
        "staff_list": staff_list,
        "groups": groups
    })


@login_required
def add_group(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only admin can add groups.")

    if request.method == "POST":
        group_name = request.POST.get("name")

        if group_name:
            if Group.objects.filter(name=group_name).exists():
                messages.error(request, "Group already exists!")
            else:
                Group.objects.create(name=group_name)
                messages.success(request, "Group added successfully!")

        return redirect("staff_management")

    return render(request, "staff/add_group.html")
def logout_view(request):
    logout(request)
    return redirect('login')