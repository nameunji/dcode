from django.urls import path
from .views      import FeedListView, FeedDetailView

urlpatterns = [
    path('', FeedListView.as_view()),
    path('/<int:feed_id>', FeedDetailView.as_view()),
]
