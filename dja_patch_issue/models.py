from django.db import models


class Article(models.Model):

    class JSONAPIMeta:
        resource_name = "article"

    def __str__(self):
        return "id={}".format(self.pk)


class Tag(models.Model):
    articles = models.ManyToManyField(
        Article,
        #through="GroupMember",
        #through_fields=("group", "user"),
        related_name="tags",
        related_query_name="tags",
    )

    class JSONAPIMeta:
        resource_name = "tag"

    def __str__(self):
        return "id={}".format(self.pk)
