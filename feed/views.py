from .models import (
    Tag,
    Feed,
    FeedThumbnail,
    FeedTag,
    FeedLike,
    FeedComment
)

from django.views import View
from django.http  import JsonResponse, HttpResponse

class FeedListView(View):
    def get(self, request):
        pageNo   = int(request.GET.get('pageNo', 0)) 
        pageSize = int(request.GET.get('pageSize', 10))

        feeds = Feed.objects.order_by('-created_at')[pageNo * pageSize : (pageNo+1) * pageSize]

        data = [{
            'id'            : feed.id,
            'tags'          : [el.tag.tag for el in FeedTag.objects.select_related('tag').filter(feed_id = feed.id)],
            'mdThumb'       : feed.md_thumb,
            'title'         : feed.title,
            'content'       : feed.content,
            'updated_at'    : feed.updated_at.strftime("%Y-%m-%d %H:%M"),
            'count_like'    : feed.count_like,
            'count_comment' : feed.count_comment,
            'count_shared'  : feed.count_shared
        } for feed in feeds]

        total_count = Feed.objects.count()

        return JsonResponse({'list': data, 'totalCount':total_count}, status = 200)


