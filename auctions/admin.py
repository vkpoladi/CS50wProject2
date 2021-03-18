from django.contrib import admin

from .models import User, listing, bid_entry, comment, watchlist_entries

# Register your models here.
admin.site.register(User)
admin.site.register(listing)
admin.site.register(bid_entry)
admin.site.register(comment)
#admin.site.register(watchlist_entries)