from django.contrib import admin
from .models import LandUsePlan
from .models import Comment
from .models import Vote

admin.site.register(LandUsePlan)
admin.site.register(Comment)
admin.site.register(Vote)