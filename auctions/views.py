from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

import datetime

from .models import User, listing, bid, comment, watchlist_entries


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

        category = request.POST.get("category","")

        status = "open"

        new_listing = listing(username=username, title=title, description=description, image_url=image_url, starting_bid_price=starting_bid_price, post_date=post_date, category=category, status=status)
        new_listing.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html", {
            "listings": listing.objects.all()
        })

def listing_page(request, listing_pk):
    listing_entry = listing.objects.get(pk=listing_pk)
    #listing_category = listing_entry.category
    #if listing_category == "None":
    #    listing_category = "No Category Listed"

    return render(request, "auctions/listing_page.html", {
        "listing": listing_entry
        #"category": listing_category
    })


def watchlist(request):
    if request.method == "POST":
        w_listing = request.POST["add_listing"]
        w_username = request.user.username
        watchlist_entry = watchlist_entries(w_listing=w_listing, w_username=w_username)
        watchlist_entry.save()

        return render(request, "auctions/listing_page.html", {
            "listing": listing.objects.get(pk=w_listing)
        })

    else:
        listings = []
        w_username = request.user.username

        try:
            w_listings = watchlist_entries.objects.filter(w_username=w_username)

            for w_listing in w_listings:
                listings.append(listing.objects.get(pk=w_listing.w_listing))

            return render(request, "auctions/watchlist.html", {
                "username":w_username,
                "listings":listings
            })

        except watchlist_entries.DoesNotExist:
            return render(request, "auctions/watchlist.html", {
            "username":w_username,
            "message":"No listings in watchlist"
            })


def watchlist_remove(request):
    r_listing_title = request.POST["watchlist_remove"]
    r_listing = listing.objects.get(title=r_listing_title)
    r_listing_pk = r_listing.pk
    watchlist_entries.objects.filter(w_listing=r_listing_pk).delete()
    return HttpResponseRedirect(reverse("watchlist"))


