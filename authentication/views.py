from base64 import urlsafe_b64encode
import email
from email.message import EmailMessage
from http.client import HTTPResponse
import imp
from lib2to3.pgen2.tokenize import generate_tokens
from operator import truediv
import re
from telnetlib import LOGOUT
from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from login1 import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from . tokens import generate_token
from django.core.mail import EmailMessage,send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode



# Create your views here.
def home(request):
    return render(request,'authentication/index.html')

def signup(request):
    if request.method == "POST":
        username =request.POST['username']
        fname =request.POST['fname']
        lname =request.POST['lname']
        email =request.POST['ename']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"user already exist please try other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"Email already exist")
            return redirect('home')

        if len(username)>10:
            messages.error(request,"username is long")

        if pass1 != pass2:
            messages.error(request,"password didnot match")

        if not username.isalnum():
            messages.error(request,"username must be alpanumeric")
            return redirect('home')


        myuser =User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()

        messages.success(request,"Account has been created succesfully, we have sent you confirmation email")

        #welcome email

        subject = "welcome to login"
        message ="hello"+ myuser.first_name + "\n Thank you for visiting \n\n Thanking you \n\n Pallavi"
        from_email =settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # email confirmation
        current_site = get_current_site(request)
        email_subject ="confirm your email"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)

        })

        email = EmailMessage(
            email_subject,message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        
        return redirect('signin')



    return render(request,'authentication/signup.html')

def signin(request):
    if request.method == "POST":
        username =request.POST['username']
        pass1 = request.POST['pass1']

        user =authenticate(username=username, password=pass1)

        if user is not None:
            login(request,user)
            fname= user.first_name
            return render(request,"authentication/index.html",{'fname':fname})
        else:
            messages.error(request,"wrong Credentials")
            return redirect('home')


    return render(request,'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request,"Logged out succesfully")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = user.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser= None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active =True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')