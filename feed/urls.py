from django.urls import path
from .views      import FeedListView

urlpatterns = [
    path('', FeedListView.as_view())
]
