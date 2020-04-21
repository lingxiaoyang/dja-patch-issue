from django.urls import path

from .views import ArticleRelationshipsViewSet, TagRelationshipsViewSet

urlpatterns = [
    path('articles/<pk>/relationships/<related_field>/', ArticleRelationshipsViewSet.as_view(), name="article-relationships"),
    path('tags/<pk>/relationships/<related_field>/', TagRelationshipsViewSet.as_view(), name="tag-relationships"),
]
