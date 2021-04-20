from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime


# Create your models here.


class Article(models.Model):
    '''
    帖子表
    '''
    title = models.CharField(max_length=255)
    # 描述
    brief = models.CharField(null=True, blank=True, max_length=255)
    category = models.ForeignKey("Category", on_delete=True)
    content = models.TextField(u"文章内容")
    author = models.ForeignKey("UserProfile", on_delete=True)
    # 时间自动生成
    # auto_now_add:保存第一次创建文章时候的时间，后面修改文章时间不改变
    pub_date = models.DateTimeField(blank=True, null=True)
    # auto_now:后面修改文章的话时间改变
    last_modify = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(u"优先级", default=1000)
    # upload_to：将图片文件存储到./uploads目录下
    head_img = models.ImageField(u"文章标题图片", upload_to="./uploads")

    status_choices = (
        ("draft", u"草稿"),
        ("published", u"已发布"),
        ("hidden", u"隐藏")
    )
    status = models.CharField(choices=status_choices, default="published", max_length=255)

    def clean(self):
        if self.status == "draft" and self.pub_date is not None:
            raise ValidationError("Draft entries may not have a publication date.")
        if self.status == "published" and self.pub_date is None:
            self.pub_date = datetime.date.today()

    def __str__(self):
        return self.title


class Comment(models.Model):
    '''
    评论表 + 点赞表
    '''
    article = models.ForeignKey(Article, verbose_name=u"所属文章", on_delete=True)
    parent_comment = models.ForeignKey("self", related_name="my_children", blank=True, null=True, on_delete=True)
    comment_choices = ((1, u"评论"),
                       (2, u"点赞"))
    comment_type = models.IntegerField(choices=comment_choices, default=1)
    user = models.ForeignKey("UserProfile", on_delete=True)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    def clean(self):
        '''
        评论的话限制内容不为空，
        :return:
        '''
        if self.comment_type == 1 and len(self.comment) == 0:
            raise ValidationError("评论内容不能为空")

    def __str__(self):
        return "%s, P:%s, %s" % (self.article, self.parent_comment.id, self.comment)


class Category(models.Model):
    '''
    板块表
    '''
    name = models.CharField(max_length=255)
    # blank表示可以为空
    brief = models.CharField(null=True, blank=True, max_length=255)
    # 板块动态展示
    set_as_top_menu = models.BooleanField(default=False)
    position_index = models.SmallIntegerField()
    # 板主
    admins = models.ManyToManyField("UserProfile", blank=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    '''
    用户表
    '''
    user = models.OneToOneField(User, on_delete=True)
    # 昵称
    name = models.CharField(max_length=255)
    signature = models.CharField(max_length=255, blank=True, null=True)
    head_img = models.ImageField(height_field=150, width_field=150, blank=True, null=True)

    def __str__(self):
        return self.name
