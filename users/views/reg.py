from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseForbidden
from django.db import transaction
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist

from users.models import RegisterToken, UserProfile
from users.utils import sorted_users, sorted_tokens, sorted_categories
from users.forms import RegisterForm
from django.contrib.auth.forms import UserCreationForm


def reg_list_token(request):
    if not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    elif not request.user.profile.is_authorized() and not request.user.profile.is_trusted():
        return redirect('index')

    filters = request.GET.getlist('find')
    groups = request.GET.get('g')
    tokens = apply_filter(filters=filters, groups=groups)

    return render(request, 'users/reg_list_token.html', {
        'tokens': sorted_tokens(tokens),
        'categories': sorted_categories,
        'filters': filters,
        'params': request.GET.urlencode(),
    })

@permission_required('auth.add_user')
def reg_add_token(request):
    if not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    elif not request.user.profile.is_authorized() and not request.user.profile.is_trusted():
        return redirect('index')
    status = ''

    if 'submit' in request.POST:
        number = request.POST.get('number')
        for tn in range(0, int(number)):
            token = RegisterToken()
            token.save()
            for group_id in request.POST.getlist('groups'):
                try:
                    token.groups.add(Group.objects.get(id=int(group_id)))
                except Group.DoesNotExist: pass
                except ValueError: pass
            token.save()

    return render(request, 'users/reg_add_token.html', {
        'categories': sorted_categories,
        'status': status,
    })


def reg_form(request, token=None):
    try:
        reg_token = RegisterToken.objects.get(token=token)
        if not reg_token.valid:
            return render(request, 'users/reg_form.html', {
                "token": token,
                "error_token": "used_token",
            })
    except ObjectDoesNotExist:
        return render(request, 'users/reg_form.html', {
            "token": token,
            "error_token": "invalid_token",
        })

    error = []
    if request.method == 'POST' and not error:
        form = RegisterForm(request.POST)
        form.instance.backend = 'django.contrib.auth.backends.ModelBackend'
        if form.is_valid():
            with transaction.atomic():
                form.save()
                reg_token.valid = False
                reg_token.user = form.instance
                reg_token.save()
                p = UserProfile()
                p.user = form.instance
                p.save()
                for g in reg_token.groups.all():
                    g.user_set.add(form.instance)
            login(request, form.instance)
            return redirect('users:edit fancy', username=form.instance.username)
        else:
            if "username" in form.errors:
                error.append("error_username")
            if "email" in form.errors:
                error.append("error_email")

    return render(request, 'users/reg_form.html', {
        "token": token,
        "error": error,
    })


def reg_edit_token(request, token=None):
    pass


def apply_filter(filters, groups, tokens=None):
    tokens = tokens or RegisterToken.objects.all()

    if 'disabled' in filters:
        tokens = tokens.filter(valid=False)
    elif 'all' not in filters:
        tokens = tokens.filter(valid=True)

    if groups:
        to_include, to_exclude = [], []
        for g in groups.split(','):
            try:
                g = int(g)
            except ValueError:
                pass
            else:
                filters.append(g)
                if g >= 0:
                    to_include.append(g)
                else:
                    to_exclude.append(-g)

        if to_include:
            tokens = tokens.filter(groups__in=to_include)

        if to_exclude:
            tokens = tokens.exclude(groups__in=to_exclude)

    return tokens

