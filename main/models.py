from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal

from .utilities import send_activation_email, get_timestamp_path


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True)
    send_massages = models.BooleanField(default=True)

    def delete(seld, *args, **kwargs):
        for bulletin in self.bulletin_set.all():
            bulletin.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True)

    order = models.SmallIntegerField(default=0, db_index=True)

    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True)


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric.name, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')


class Bulletin(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT)

    title = models.CharField(max_length=40)

    content = models.TextField()

    price = models.FloatField(default=0)

    contacts = models.TextField()

    image = models.ImageField(blank=True, upload_to=get_timestamp_path)

    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True, db_index=True)

    published = models.DateTimeField(auto_now_add=True, db_index=True)

    def delete(self, *args, **kwargs):
        for img in self.additionalimage_set.all():
            img.delete()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ('-published',)


class AdditionalImage(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.CASCADE)

    image = models.ImageField(upload_to=get_timestamp_path)


class Comment(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.CASCADE)

    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created_at',)




user_registrated = Signal(providing_args=('instance'))

def user_registrated_dispatcher(sender, **kwargs):
    send_activation_email(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)
