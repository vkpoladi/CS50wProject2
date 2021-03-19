from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

import datetime

from .models import User, listing, comment, watchlist_entries, bid_entry


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

    #Find current max bid price if it exists
    #current_bids = bid.objects.filter(listing=listing_entry)

    current_bids = listing_entry.bids.all()
    current_bid_price = 0.00
    current_bid = None

    for bid in current_bids:
        if bid.bid_price > current_bid_price:
            current_bid_price = bid.bid_price
            current_bid = bid 

    if current_bid != None:
        current_bid_message = f"Current leading bid is {current_bid_price} by {current_bid.username}"
    else:
        current_bid_message = ""

    return render(request, "auctions/listing_page.html", {
        "listing": listing_entry,
        "current_bid_message": current_bid_message 
        #"category": listing_category

    })


def watchlist(request):
    if request.method == "POST":
        w_listing = request.POST["add_listing"]
        w_username = request.user.username
        watchlist_entry = watchlist_entries(w_listing=w_listing, w_username=w_username)
        watchlist_entry.save()
        
        #listing_entry = listing.objects.get(pk=w_listing)

        return HttpResponseRedirect(reverse("listing_page", args=(w_listing,)))

        #return render(request, "auctions/listing_page.html", {
        #    "listing": listing.objects.get(pk=w_listing)
        #})

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

def bidding(request):
    bid_price = request.POST["bid_amount"]
    listing_title = request.POST["bid_listing"]

    listing_entry = listing.objects.get(title=listing_title)

    listing_pk = listing_entry.pk
    username = request.user.username
    bid_date = datetime.datetime.now()
    starting_bid_price = listing_entry.starting_bid_price
    
    #current_bids = bid.objects.filter(listing=listing)
    current_bids = listing_entry.bids.all()
    current_bid_price = 0.00
    current_bid = None

    for bid in current_bids:
        if bid.bid_price > current_bid_price:
            current_bid_price = bid.bid_price
            current_bid = bid

    if bid_price == "":
        bid_price = 0.00
    else:
        bid_price = (float) (request.POST["bid_amount"])


    if current_bid != None:
        current_bid_message = f"Current leading bid is {current_bid_price} by {current_bid.username}"
    else:
        current_bid_message = ""

    #Error checking for new bid price submission

    if bid_price >= 100000000 or bid_price < 0:
        return render(request, "auctions/listing_page.html", {
            "listing": listing.objects.get(pk=listing_entry.pk),
            "current_bid_message": current_bid_message,
            "message": "Bid price is outside of valid range. Please try again."
        })    

    if current_bid != None and bid_price <= current_bid_price:
        return render(request, "auctions/listing_page.html", {
            "listing": listing.objects.get(pk=listing_entry.pk),
            "current_bid_message": current_bid_message,
            "message": f"Bid price must be higher than current leading bid price of {current_bid_price}. Please try again."
        })

    if bid_price < starting_bid_price:
        return render(request, "auctions/listing_page.html", {
            "listing": listing.objects.get(pk=listing_entry.pk),
            "current_bid_message": current_bid_message,
            "message": "Bid price must be at minimum the starting bid price. Please try again."
        })
       
    #If passed error checking, process new bid request
    new_bid = bid_entry(listing=listing_entry, username=username, bid_date=bid_date, bid_price=bid_price)
    new_bid.save()

    current_bid_message = f"Current leading bid is {bid_price} by {username}"

    return render(request, "auctions/listing_page.html", {
        "listing": listing.objects.get(pk=listing_pk),
        "current_bid_message": current_bid_message,
        "message": "Bid successfully placed."
    }) 





def categories(request):
    categories = listing.objects.values('category')
    distinct_categories = set(val for dic in categories for val in dic.values())


    return render(request, "auctions/categories.html", {
        "categories": distinct_categories
    })

def category_page(request, category):
    listings = listing.objects.filter(category=category)

    return render(request, "auctions/category_page.html", {
        "listings": listings
    })
    

