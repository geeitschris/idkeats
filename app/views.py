from django.shortcuts import render, redirect
from .models import *
import bcrypt
from django.contrib import messages
import urllib
import requests
import json
from django.http import HttpResponse
import random

YELP_API_KEY = "hqNC6-38oblTgENX-snoVNZ_lzBFzAhfInxMbnLLxBK5RoBWSWuU85MF65zvly-kEP0VM0oEqhciGGNJ4M1_amSEnIUg1UCa5JUEGa5HqlBNkPKc4HsQOQoGEFQvXnYx"

API_URL = "https://api.yelp.com/v3/businesses/"

headers = {'Authorization': f'Bearer {YELP_API_KEY}'}


def index(request):
    return render(request, 'login.html')


def register(request):
    return render(request, "registration.html")


def createuser(request):
    errors = User.objects.validator(request.POST)
    if len(errors) > 0:
        for k, v in errors.items():
            messages.error(request, v)
        return render(request, 'registration.html')
    password = request.POST['password']
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = User.objects.create(first_name=request.POST['first_name'].lower().title(),
                                   last_name=request.POST['last_name'].lower().title(), email=request.POST['email'], password=hashed_pw)
    request.session['userid'] = new_user.id
    return redirect('/success')


def dashboard(request):
    if request.session.get('userid') is None:
        return redirect('/')
    user = User.objects.filter(id=request.session['userid'])
    context = {
        "user": user[0]
    }
    return render(request, "dashboard.html", context)


def login(request):
    errors = {}
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    if len(request.POST['email']) == "" or not EMAIL_REGEX.match(request.POST['email']):
        errors['email'] = 'Invalid E-Mail'
    if len(request.POST['password']) < 8:
        errors['password'] = 'Password must be at least 8 characters'
    user = User.objects.filter(email=request.POST['email'])
    if user:
        logged_user = user[0]
        if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
            request.session['userid'] = logged_user.id
            return redirect('/success')
    for k, v in errors.items():
        messages.error(request, v)
    return render(request, 'login.html')


def logout(request):
    request.session.clear()
    return redirect('/')


def addfavorites(request, id):
    if request.session.get('userid') is None:
        return redirect('/')
    current_user = User.objects.filter(id=request.session['userid']).first()
    if len(Restaurant.objects.filter(business_id=id)) > 0:
        return redirect(f'/favorites/add/{id}/success')
    new_rest = Restaurant.objects.create(business_id=id)
    new_rest.user.add(current_user)
    return redirect(f'/favorites/add/{id}/success')


def favorites(request, id):
    if request.session.get('userid') is None:
        return redirect('/')
    current_user = User.objects.filter(id=request.session['userid']).first()
    favorites_list = current_user.user_favorited.all()
    favorites_list_info = []
    for business in favorites_list:
        req = requests.get(API_URL+business.business_id, headers=headers)
        business_now = json.loads(req.text)
        favorites_list_info.append(business_now)
        print(req)
    context = {
        'user': current_user,
        'favorites': favorites_list_info
    }
    print(len(context['favorites']))
    return render(request, "favorites.html", context)


def removeFave(request, bizid):
    if request.session.get('userid') is None:
        return redirect('/')
    current_user = User.objects.filter(id=request.session['userid']).first()
    biz_to_Remove = Restaurant.objects.get(business_id=bizid)
    biz_to_Remove.user.remove(current_user)
    return redirect(f'/favorites/{current_user.id}')


def decideForMe(request, lat, lng):
    if request.session.get('userid') is None:
        return redirect('/')
    current_user = User.objects.filter(id=request.session['userid']).first()
    myurl = "https://api.yelp.com/v3/businesses/search?term=food&latitude=" + \
        lat + "&longitude=" + lng + "&limit=20&radius=1750"
    x = headers
    res = requests.get(myurl, headers=x)
    res = res.json()
    choice = random.randint(0, 19)
    print('*'*100)
    for shop in range(len(res['businesses'])):
        if shop == choice:
            pick = res['businesses'][shop]
    print(pick)
    context = {
        'user': current_user,
        'pick': pick,
        'lat': lat,
        'long': lng
    }
    return render(request, 'random.html', context)
