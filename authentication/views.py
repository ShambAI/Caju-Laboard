# -*- encoding: utf-8 -*-
"""
Copyright (c) 2021 - present Technoserve x Damilola
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import RemOrganization, RemRole, RemUser, Plantation
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm, FullSignUpForm, RegisterOrganization, RegisterRole
from . import models
from . import utils

import datetime
import logging
import uuid

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.core.mail import EmailMessage

from authentication import forms

logger = logging.getLogger(__name__)
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm, FullSignUpForm
from django.template import loader, Context
from . import forms as custom_forms


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def login_view(request):

    msg = None

    if request.method == "POST":
        form = LoginForm(data = request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
                # rem_user = RemUser.objects.filter(user_name=username)
                # _pass = rem_user.values()[0]['password']
                # if password == _pass:
                #     login(request, user)
                #     return redirect("/")
                # else:
                #     msg = 'Invalid credentials'   
        else:
            msg = str(form.errors) #'Error validating the form'
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, "msg" : msg, 'segment': 'login'})

def forgot_password(request):

    msg     = None
    success = False

    if request.method == 'POST':
        form = custom_forms.ForgotPassword(request.POST)
        if form.is_valid():

            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset your Password'
            message = loader.get_template('accounts/password_reset_email.html').render(
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                }
            )
            # message = render_to_string('accounts/acc_active_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token':account_activation_token.make_token(user),
            # })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, 
                message,
                from_email= '"Caju-Lab Support" <cajusupport@tnslabs.org>',
                to=[to_email]
            )
            email.content_subtype = "html"

            email.send()

            msg     = "We've emailed you instructions for setting your password. \
                        If an account exists with the email you have entered, you should receive them shortly.\
                        If you don't receive an email, please make sure you've entered the address you registered with correctly, \
                        and check your spam folder."
            success = True
            # return HttpResponse('Please confirm your email address to complete the registration')
        else:
            msg = 'Form is not valid'
    else:
        form = custom_forms.ForgotPassword()
    return render(request, 'accounts/password_reset_form.html', {"form": form, "msg" : msg, "success" : success})

def password_reset_confirm(request, uidb64, token):
    
    context = {}
    try:
        # uid = force_text(urlsafe_base64_decode(uidb64))
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):

        
        msg     = None
        success = False

        if request.method == 'POST':

            form = custom_forms.NewPassword(request.POST)

            if form.is_valid():

                password = form.cleaned_data.get("password")
                user.set_password(password)

                user.save()


                msg     = 'Password change successful. Now you can'
                success = True
                # return HttpResponse('Please confirm your email address to complete the registration')
            else:
                msg = 'Form is not valid'
        else:
            form = custom_forms.NewPassword()
        return render(request, 'accounts/new_password.html', {"form": form, "msg" : msg, "success" : success})
    else:
        html_template = loader.get_template( 'accounts/password_change_failed.html' )
        return HttpResponse(html_template.render(context, request))


def register_user(request):
    
    msg     = None
    success = False

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            phone = form.cleaned_data.get("phone")
            organization = form.cleaned_data.get("organization")
            role = form.cleaned_data.get("role")

            sec_user = RemUser(
                username=username, 
                email = email,
                first_name = first_name,
                last_name = last_name,
                phone = phone,
                organization = organization,
                role = role,
                
            )

            sec_user.save()



            current_site = get_current_site(request)
            mail_subject = 'Activate your Cashew Remote Sensing account.'
            message = loader.get_template('accounts/acc_active_email.html').render(
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                }
            )
            # message = render_to_string('accounts/acc_active_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token':account_activation_token.make_token(user),
            # })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, 
                message, 
                from_email = '"Caju-Lab Support" <cajusupport@tnslabs.org>',
                to=[to_email]
            )
            email.content_subtype = "html"

            email.send()

            msg     = 'Please confirm your email address to complete the registration'
            success = True
            # return HttpResponse('Please confirm your email address to complete the registration')
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {"form": form, "msg" : msg, "success" : success})

def activate(request, uidb64, token):
    
    context = {}
    try:
        # uid = force_text(urlsafe_base64_decode(uidb64))
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user)
        html_template = loader.get_template( 'email_confirmed.html' )
        return HttpResponse(html_template.render(context, request))
    else:
        html_template = loader.get_template( 'email_confirm_invalid.html' )
        return HttpResponse(html_template.render(context, request))

# def register_user(request):

#     msg     = None
#     success = False

#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get("username")
#             raw_password = form.cleaned_data.get("password1")
#             user = authenticate(username=username, password=raw_password)

#             msg     = 'User created - please <a href="/login">login</a>.'
#             success = True
            
#             #return redirect("/login/")

#         else:
#             msg = 'Form is not valid'    
#     else:
#         form = SignUpForm()

#     return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })

def register_user_full(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = FullSignUpForm(request.POST)
        if form.is_valid():
            
            raw_password1 = form.cleaned_data.get("password1")
            raw_password2 = form.cleaned_data.get("password2")

            if raw_password1 == raw_password2:
                current_user = request.user
                # id = uuid.uuid4().int
                obj = form.save(commit=False)
                obj.created_by = current_user.id
                obj.created_date = datetime.datetime.now()
                obj.updated_by = current_user.id
                obj.updated_date = datetime.datetime.now()

                org_name = form.cleaned_data.get("organization_name")
                obj.organization = org_name
                
                email = form.cleaned_data.get("email")
                obj.e_mail = email

                # obj.id = id

                obj.password = raw_password1


                obj.save()
                # username = form.cleaned_data.get("username")
                # raw_password = form.cleaned_data.get("password1")
                # user = authenticate(username=username, password=raw_password)

                user_name = form.cleaned_data.get("user_name")
                email = form.cleaned_data.get("email")

                sec_user = User(username=user_name, email = email)
                sec_user.set_password(raw_password1)

                sec_user.save()

                msg     = 'User created - please <a href="/login">login</a>.'
                success = True
                
                #return redirect("/login/")
            
            else:
                msg = 'Form is not valid - Passwords do not match'

        else:
            msg = 'Form is not valid'    
    else:
        form = FullSignUpForm()

    return render(request, "accounts/full_login.html", {"form": form, "msg" : msg, "success" : success })

# @login_required(login_url="/login/")
def register_org(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = RegisterOrganization(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                current_user = request.user
                if current_user.is_authenticated:
                    # Do something for authenticated users.
                    obj.created_by = current_user.id
                    obj.created_date = datetime.datetime.now()
                    obj.updated_by = current_user.id
                    obj.updated_date = datetime.datetime.now()
                    
                    #return redirect("/login/")
            except:
                print("")
            
            obj.save()
            msg     = 'Organization created - please <a href="/register">register user</a>.'
            success = True

        else:
            msg = 'Form is not valid'    
    else:
        form = RegisterOrganization()

    return render(request, "accounts/register_org.html", {"form": form, "msg" : msg, "success" : success })

@login_required(login_url="/login/")
def register_role(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = RegisterRole(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data.get("organization_")
            print(org_name)
            current_user = request.user
            if current_user.is_authenticated:
                # Do something for authenticated users.
                obj = form.save(commit=False)

                org_name = form.cleaned_data.get("organization_")
                # print(org_name)

                # logger.info("The value of org name is %s", org_name)

                # org = RemOrganization.objects.filter(id = org_name)[0]
                obj.organization = org_name
                obj.created_by = current_user.id
                obj.created_date = datetime.datetime.now()
                obj.updated_by = current_user.id
                obj.updated_date = datetime.datetime.now()
                obj.save()

                msg     = 'Role added - please <a href="/register">register user</a>.'
                success = True
                
                #return redirect("/login/")
            else:
                # Do something for anonymous users.
                msg     = 'Role not added - please <a href="/register_role">try againh</a>.'
                success = False

        else:
            msg = 'Form is not valid'    
    else:
        form = RegisterRole()

    return render(request, "accounts/register_role.html", {"form": form, "msg" : msg, "success" : success })

@login_required(login_url="/login/")
def load_roles(request):
    org_id = request.GET.get('organization_name')
    roles = RemRole.objects.filter(organization=org_id)
    return render(request, 'accounts/role_options.html', {'roles': roles})

@login_required(login_url="/login/")
def profile(request):
    rem_user = RemUser.objects.filter(username=request.user.username)
    rem_org = RemOrganization.objects.filter(id = rem_user.values()[0]['organization_id'])

    context = rem_user.values()[0]

    try:
        context['organization_name'] = rem_org.values()[0]['organization_name']
    except:
        context['organization_name'] = ''
    return render(request, 'profile.html', context)

# @login_required(login_url="/login/")
# def tables(request):
#     context = {}
    
#     context['segment'] = 'tables'
#     return render(request, 'tables.html', context)

@login_required(login_url="/login/")
def tables(request):
    context = {}
    companies = RemOrganization.objects.all()
    org_count = int(companies.count() / 10)

    plantations = Plantation.objects.all()
    plantation_count = int(plantations.count() / 10)

    context['companies'] = companies
    context['org_count'] = range(1, org_count)
    context['org_count'] = range(1, org_count)
    context['plantation_count'] = range(1, plantation_count)
    context['segment'] = 'tables'
    return render(request, 'companies.html', context)

@login_required(login_url="/login/")
def yields(request):
    context = {}
    yields_list = models.YieldHistory.objects.filter(status = utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(yields_list, 10)
    
    page_range = paginator.get_elided_page_range(number=page)
    try:
        yields = paginator.page(page)
    except PageNotAnInteger:
        yields = paginator.page(1)
    except EmptyPage:
        yields = paginator.page(paginator.num_pages)

    context['yields'] = yields
    context['segment'] = 'yield'
    context['page_range'] = page_range
    return render(request, 'yield.html', context)

@login_required(login_url="/login/")
def plantations(request):
    context = {}
    plantations_list = models.Plantation.objects.filter(status = utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(plantations_list, 10)
    
    page_range = paginator.get_elided_page_range(number=page)
    try:
        plantations = paginator.page(page)
    except PageNotAnInteger:
        plantations = paginator.page(1)
    except EmptyPage:
        plantations = paginator.page(paginator.num_pages)

    context['plantations'] = plantations
    context['segment'] = 'plantations'
    context['page_range'] = page_range

    return render(request, 'plantations.html', context)

@login_required(login_url="/login/")
def nurseries(request):
    context = {}
    nurseries_list = models.Nursery.objects.filter(status = utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(nurseries_list, 10)
    
    page_range = paginator.get_elided_page_range(number=page)
    try:
        nurseries = paginator.page(page)
    except PageNotAnInteger:
        nurseries = paginator.page(1)
    except EmptyPage:
        nurseries = paginator.page(paginator.num_pages)

    context['nurseries'] = nurseries
    context['segment'] = 'nurseries'
    context['page_range'] = page_range
    return render(request, 'nurseries.html', context)

@login_required(login_url="/login/")
def shipment(request):
    context = {}
    nurseries_list = models.Nursery.objects.filter(status = utils.Status.ACTIVE)

    page = request.GET.get('page', 1)

    paginator = Paginator(nurseries_list, 10)
    
    page_range = paginator.get_elided_page_range(number=page)
    try:
        nurseries = paginator.page(page)
    except PageNotAnInteger:
        nurseries = paginator.page(1)
    except EmptyPage:
        nurseries = paginator.page(paginator.num_pages)

    context['nurseries'] = nurseries
    context['segment'] = 'nurseries'
    context['page_range'] = page_range
    return render(request, 'shipment.html', context)
