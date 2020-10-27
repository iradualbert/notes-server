from django.contrib import admin
from .models import (
    Channel,
    Product,
    Listing,
    Branch,
    ChannelAdmin,
    Question,
    Answer,
    Review,
    Subscription,
    Link
)


admin.site.register(Product)
admin.site.register(Channel)
admin.site.register(Subscription)
admin.site.register(ChannelAdmin)
admin.site.register(Branch)
admin.site.register(Listing)
admin.site.register(Review)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Link)