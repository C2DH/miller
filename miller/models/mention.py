from django.db import models

class Mention(models.Model):
    from_story = models.ForeignKey('miller.Story', related_name='from_mentions', on_delete=models.CASCADE)
    to_story = models.ForeignKey('miller.Story', related_name='to_mentions', on_delete=models.CASCADE)
    date_created = models.DateField(auto_now=True)

    class Meta:
        ordering = ["-date_created"]
        verbose_name_plural = "mentions"

    def __str__(self):
        return f'{self.from_story} -> {self.to_story}'
