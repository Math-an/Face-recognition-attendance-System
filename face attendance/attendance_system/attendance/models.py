from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission, PermissionsMixin
from django.db import models
from django.conf import settings

# Manager for the Admin model
class AdminManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(username, email, password, **extra_fields)

# Admin model
class Admin(AbstractUser, PermissionsMixin):
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="admin_groups",
        blank=True,
        help_text="The groups this admin belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="admin_permissions",
        blank=True,
        help_text="Specific permissions for this admin.",
        verbose_name="user permissions",
    )

    objects = AdminManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


# Custom User model
class User(AbstractUser):
    name = models.CharField(max_length=100, blank=True, null=True)  # 'name' field
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # 'phone_number' field
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('staff', 'Staff'), ('student', 'Student')], default='student')  # 'role' field
    dob = models.DateField(blank=True, null=True)  # 'dob' (date of birth) field
    

    def __str__(self):
        return self.username


# Attendance model
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Use custom user model
    date = models.DateField(auto_now_add=True)
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'date')  # Ensure one record per user per day

    def __str__(self):
        return f"{self.user.username} - {self.date} - {'Present' if self.is_present else 'Absent'}"
