from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

import datetime

from .models import User, listing, bid, comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings":listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method == "POST":
        
        user = request.user

        username = user.username
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        
        starting_bid_price = request.POST["starting_bid_price"]

        #Error checking for starting bid price
        if starting_bid_price == "":
            starting_bid_price = 0
        else:
            starting_bid_price = (float) (request.POST["starting_bid_price"])
        
        if starting_bid_price >= 100000000 or starting_bid_price < 0:
            return render(request, "auctions/create_listing.html", {
                "listings": listing.objects.all(),
                "message": "Invalid starting bid price"
            })

        post_date = datetime.datetime.now()
        category = request.POST["category"]
        status = "open"

        new_listing = listing(username=username, title=title, description=description, image_url=image_url, starting_bid_price=starting_bid_price, post_date=post_date, category=category, status=status)
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html", {
            "listings": listing.objects.all()
        })

def listing_page(request, listing_pk):
    return render(request, "auctions/listing_page.html", {
        "listing": listing.objects.get(pk=listing_pk)
    })
