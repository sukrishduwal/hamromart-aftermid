from pyexpat.errors import messages
from tokenize import group

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied


@login_required
def staff_management(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only admin can access staff management.")

    # Get all staff users (users in any group)
    staff_list = User.objects.filter(groups__isnull=False).distinct()

    groups = Group.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        group_id = request.POST.get("group")
        # 🚨 Check duplicate username
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

        # Staff can access Django admin only if needed
        user.groups.add(group)
        user.save()

        return redirect("staff_management")

    return render(request, "staff/staff_management.html", {
        "staff_list": staff_list,
        "groups": groups
    })