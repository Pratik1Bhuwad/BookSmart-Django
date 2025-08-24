# services/models.py
from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='service_category_images/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

class ServiceSubCategory(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='service_subcategory_images/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Service Sub-categories'

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class Service(models.Model):
    name = models.CharField(max_length=100, help_text="Generic name of the service (e.g., 'Haircut')")
    sub_category = models.ForeignKey(ServiceSubCategory, on_delete=models.CASCADE, related_name='services')

    class Meta:
        unique_together = ('name', 'sub_category')
    
    def __str__(self):
        return f"{self.name} ({self.sub_category.name})"
