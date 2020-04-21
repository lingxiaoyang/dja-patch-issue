from rest_framework_json_api.views import RelationshipView

from .models import Article, Tag


class ArticleRelationshipsViewSet(RelationshipView):
    queryset = Article.objects.all()


class TagRelationshipsViewSet(RelationshipView):
    queryset = Tag.objects.all()
