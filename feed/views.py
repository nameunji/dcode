import json

from utils   import login_decorator 
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
        if pageSize > 10: pageSize = 10

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

class FeedDetailView(View):
    @login_decorator
    def get(self, request, feed_id):
        try:
            feed = Feed.objects.prefetch_related('feedthumbnail_set').get(id = feed_id)
            data = {
                'id'            : feed.id,
                'tags'          : [ el['tag'] for el in feed.tag.values() ],
                'mdThumb'       : [ el['url'] for el in feed.feedthumbnail_set.values() ],
                'title'         : feed.title,
                'content'       : feed.content,
                'updated_at'    : feed.updated_at.strftime("%Y-%m-%d %H:%M"),
                'count_like'    : feed.count_like,
                'count_comment' : feed.count_comment,
                'count_shared'  : feed.count_shared,
                'user_like'     : False
            }
            if hasattr(request, 'user'):
                user = request.user.id
                feedlike = FeedLike.objects.filter(feed_id = feed_id, user_id = user)
                if feedlike.exists():
                    data['user_like'] = True
            return JsonResponse({'data': data}, status = 200)
        except Feed.DoesNotExist:
            return JsonResponse({'message' : 'DOES_NOT_EXIST_FEED'}, status = 400)


class LikeView(View):
    @login_decorator
    def put(self, request, feed_id):
        user = request.user
        feedlike = FeedLike.objects.filter(feed_id = feed_id, user_id = user.id)
        if not feedlike.exists():
            FeedLike(
                feed_id = feed_id,
                user_id = user.id
            ).save()
            # feed.count_like +1
            feed = Feed.objects.get(id = feed_id).count_like
            feed += 1
            result = True
            return JsonResponse({'message': result}, status = 200)
        else:
            return JsonResponse({'message': 'ALREADY_EXIST'}, status = 400)
    
    @login_decorator
    def delete(self, request, feed_id):
        try:
            user = request.user
            like = FeedLike.objects.get(feed_id = feed_id, user_id = user.id)
            like.delete()
            # feed.count_like -1
            feed = Feed.objects.get(id = feed_id).count_like
            feed -= 1
            result = False
            return JsonResponse({'message': result}, status = 200)
        except FeedLike.DoesNotExist:
            return JsonResponse({'message': 'DOES_NOT_OPTION'}, status = 400)


class SharedView(View):
    def put(self, request, feed_id):
        try:
            feed = Feed.objects.get(id = feed_id)
            feed.count_shared += 1
            feed.save()
            return HttpResponse(status = 200)
        except Feed.DoesNotExist:
            return JsonResponse({'message': 'DOES_NOT_FEED'}, status = 400)


class Comment(object):
    def __init__(self, data, parent, user):
        self.id         = data.id
        self.user_id    = data.user_id
        self.user_name  = User.objects.get(id = data.user_id).nickname
        self.comment    = data.comment
        self.created_at = data.created_at.strftime("%Y-%m-%d %H:%M")
        self.updated_at = data.updated_at.strftime("%Y-%m-%d %H:%M")
        self.editable   = data.user_id == user
        if parent:
            child_comments = FeedComment.objects.filter(parent = data.id)
            self.reply = [Comment(comment, False, user).__dict__ for comment in child_comments]

class CommentView(View):
    # 조회
    @login_decorator
    def get(self, request, feed_id):
        if hasattr(request, 'user') : user = request.user.id
        else : user = 0
        
        parent_comments = FeedComment.objects.filter(feed_id = feed_id, parent__isnull = True)
        comments = [Comment(comment, True, user).__dict__ for comment in parent_comments]
                
        return JsonResponse({'data': comments}, status = 200)

    # 삽입
    @login_decorator
    def post(self, request, feed_id):
        user = request.user
        data = json.loads(request.body)
        if 'parent' in data:
            FeedComment(
                feed_id = feed_id,
                user_id = user.id,
                comment = data["comment"],
                parent  = data["parent"]
            ).save()
        else:
            FeedComment(
                feed_id = feed_id,
                user_id = user.id,
                comment = data["comment"],
            ).save()
        
        feed = Feed.objects.get(id = feed_id)
        feed.count_comment += 1
        feed.save()

        return HttpResponse(status = 200)

    # 수정
    @login_decorator
    def put(self, request, feed_id):
        user = request.user
        data = json.loads(request.body)
        comment_id = int(request.GET.get('comment_id', 0))

        # feed.count_comment +1
        comment = FeedComment.objects.get(id = comment_id)
        comment.comment = data["comment"]
        comment.save()
        
        return HttpResponse(status = 200)

    # 삭제
    @login_decorator
    def delete(self, request, feed_id):
        user = request.user
        comment_id = int(request.GET.get('comment_id', 0))
        comment = FeedComment.objects.get(id = comment_id)
        comment.delete()

        # feed.count_comment -1
        feed = Feed.objects.get(id = feed_id)
        feed.count_comment -= 1
        feed.save()

        return HttpResponse(status = 200)