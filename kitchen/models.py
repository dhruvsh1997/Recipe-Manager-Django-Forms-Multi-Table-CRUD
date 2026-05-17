from django.db import models
from django.utils import timezone
from datetime import timedelta


class SoftDeleteManager(models.Manager):
    """Default manager — hides soft-deleted rows from every query."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Escape-hatch manager — returns everything, including deleted."""
    def get_queryset(self):
        return super().get_queryset()


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True   # no DB table for this base class itself

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    @property
    def is_recoverable(self):
        if not self.is_deleted or not self.deleted_at:
            return False
        return timezone.now() < self.deleted_at + timedelta(days=1)

   
# Create your models here.
class Recipe(SoftDeleteModel):
    name = models.CharField(max_length=150)
    cuisine = models.CharField(max_length=80)
    prep_minutes = models.PositiveIntegerField()
    instructions = models.TextField()

    def __str__(self):
        return self.name


class Ingredient(SoftDeleteModel):
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)   # "2 cups", "1 tbsp"