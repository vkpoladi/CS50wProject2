from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=64, default="")
    middle_name = models.CharField(max_length=64, default="")
    last_name = models.CharField(max_length=64, default="")


    def __str__(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

class listing(models.Model):
    #Autofield is primary key by default and auto-increments
    username = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    image_url = models.URLField(blank=True)
    starting_bid_price = models.DecimalField(max_digits=10,decimal_places=2)
    post_date = models.DateTimeField()
    category = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=6)

    def __str__(self):
        return f"Title: {self.title}    Description:{self.description}"

class bid(models.Model):
    #Autofield is primary key by default and auto-increments
    listing = models.ForeignKey(listing, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateTimeField()
    bid_price = models.DecimalField(max_digits=10,decimal_places=2)
    username = models.CharField(max_length=64)

    def __str__(self):
        return f"Bid ${self.bid_price} on {self.listing} on {self.bid_date} by {self.username}"


class comment(models.Model):
    #Autofield is primary key by default and auto-increments
    listing = models.ForeignKey(listing, on_delete=models.CASCADE, related_name="comments")
    comment_date = models.DateTimeField()
    comment = models.CharField(max_length=500)
    username = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.username} commented on {self.listing} on {self.comment_date}"

class watchlist_entries(models.Model):
    #Autofield is primary key by default and auto-increments
    w_listing = models.IntegerField()
    w_username = models.CharField(max_length=64)

    def __str__(self):
        return f"Listing {self.w_listing} is on {self.w_username}'s watchlist"


    
