from django.db import models

class Caption(models.Model):
    document = models.ForeignKey('miller.Document', on_delete=models.CASCADE)
    story = models.ForeignKey('miller.Story', on_delete=models.CASCADE)
    date_created = models.DateField(auto_now=True)
    contents = models.TextField(blank=True, default='')

    class Meta:
        ordering = ["-date_created"]
        verbose_name_plural = "captions"

    def __str__(self):
        return f"{self.story} -> {self.document}"