from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid
from datetime import date

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100,validators=
                [RegexValidator(
                regex='^[a-zA-Z\s\-]+$',
                message='full ')],verbose_name='ФИО')
    USER_TYPE_CHOICES = (
        ('client'),
        ('admin'),
    )
    user_type = models.CharField(max_length=10,choices=USER_TYPE_CHOICES,default='client',verbose_name='user_type')
    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        """String for representing the Model object"""
        return f'{self.last_name}, {self.first_name}'

    def get_absolute_url(self):
        """Returns the URL to access a particular user instance."""
        from django.urls import reverse
        return reverse('user-detail', args=[str(self.id)])


class Category(models.Model):

    name = models.CharField(max_length=200,help_text="Enter the application category (e.g., 3D design, Sketch, etc.)")
    is_active = models.BooleanField(default=True, verbose_name='active')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'category'


class DesignRequest(models.Model):
    """
    Model representing a design request.
    """
    title = models.CharField(max_length=200, verbose_name='name')
    description = models.TextField(max_length=1000,help_text='Enter a description of the room and design preferences')
    client = models.ForeignKey(CustomUser,on_delete=models.CASCADE,verbose_name='client',related_name='design_requests')
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,help_text='Select a category for this application')
    #(аналогично status у BookInstance)

    STATUS_CHOICES = (
        ('new',),
        ('in_progress',),
        ('completed',),
    )
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='new',help_text='Application status')
    plan_image = models.ImageField(upload_to='plans/%Y/%m/%d/',verbose_name='Room plan')
    design_image = models.ImageField(upload_to='designs/%Y/%m/%d/',verbose_name='Design-project',blank=True,null=True)
    admin_comment = models.TextField(verbose_name='Admin comment',blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creation date')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Update date')


    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text='Unique ID for this application'
    )

    class Meta:
        ordering = ['-created_at']
        permissions = (
            ("can_change_status",),
            ("can_view_all",),
        )

    def __str__(self):
        return self.title

    def display_category(self):
        """
        Creates a string for the Category. This is required to display category in Admin.
        """
        return self.category.name if self.category else ''

    display_category.short_description = 'category'

    def display_client(self):
        """Аналогично display_author()"""
        return str(self.client)

    display_client.short_description = 'client'

    def get_absolute_url(self):
        """
        Returns the url to access a particular request instance.
        Как у Book и Author.
        """
        from django.urls import reverse
        return reverse('request-detail', args=[str(self.id)])

    @property
    def can_be_deleted(self):
        """(аналогично is_overdue у BookInstance)"""
        return self.status == 'new'

    def take_to_work(self, comment):
        """Принять заявку в работу"""
        if self.status != 'new':
            return False
        self.status = 'in_progress'
        self.admin_comment = comment
        self.save()
        return True

    def complete(self, design_image):
        """Завершить заявку"""
        if self.status != 'new':
            return False
        self.status = 'completed'
        self.design_image = design_image
        self.save()
        return True