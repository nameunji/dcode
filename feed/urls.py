from django.urls import path
from .views      import FeedListView, FeedDetailView, LikeView, SharedView, CommentView

urlpatterns = [
    path('', FeedListView.as_view()),
    path('/<int:feed_id>', FeedDetailView.as_view()),
    path('/<int:feed_id>/like', LikeView.as_view()),
    path('/<int:feed_id>/shared', SharedView.as_view()),
    path('/<int:feed_id>/comment', CommentView.as_view())
]
