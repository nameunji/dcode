from django.db import models

class Tag(models.Model):
    tag = models.CharField(max_length = 100, unique = True)

    class Meta:
        db_table = 'tags'

class Feed(models.Model):
    title         = models.CharField(max_length = 300)
    content       = models.TextField()
    md_thumb      = models.URLField(max_length = 2000)
    md_name       = models.CharField(max_length = 100)
    created_at    = models.DateTimeField(auto_now_add = True)
    updated_at    = models.DateTimeField(auto_now = True)
    count_like    = models.SmallIntegerField()
    count_comment = models.SmallIntegerField()
    count_shared  = models.SmallIntegerField()

    tag           = models.ManyToManyField(Tag, through = 'FeedTag')

    class Meta:
        db_table = 'feeds'

class FeedThumbnail(models.Model):
    feed = models.ForeignKey('Feed', on_delete = models.SET_NULL, null = True)
    url  = models.URLField(max_length = 2000)

    class Meta:
        db_table = 'feed_thumbnails'

class FeedTag(models.Model):
    feed = models.ForeignKey('Feed', on_delete = models.CASCADE)
    tag  = models.ForeignKey('Tag', on_delete = models.CASCADE)

    class Meta:
        db_table = 'feed_tags'

class FeedLike(models.Model):
    feed    = models.ForeignKey('Feed', on_delete = models.CASCADE)
    user_id = models.PositiveIntegerField()

    class Meta:
        db_table = 'feed_likes'

class FeedComment(models.Model):
    feed       = models.ForeignKey('Feed', on_delete = models.CASCADE)
    user_id    = models.PositiveIntegerField()
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    parent     = models.PositiveIntegerField(null = True)

    class Meta:
        db_table = 'feed_comments'

