from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ─────────────────────────────────────────────────────────────
# OFFICER ROLES
# ─────────────────────────────────────────────────────────────
class OfficerRole(models.TextChoices):
    ADMIN           = 'admin',          'Admin'
    SUPERINTENDENT  = 'superintendent', 'Superintendent'
    DETECTIVE       = 'detective',      'Detective'
    OFFICER         = 'officer',        'Officer'
    ANALYST         = 'analyst',        'Analyst'


# ─────────────────────────────────────────────────────────────
# OFFICER RANK
# ─────────────────────────────────────────────────────────────
class OfficerRank(models.TextChoices):
    CONSTABLE           = 'constable',          'Constable'
    CORPORAL            = 'corporal',           'Corporal'
    SERGEANT            = 'sergeant',           'Sergeant'
    INSPECTOR           = 'inspector',          'Inspector'
    SUPERINTENDENT      = 'superintendent',     'Superintendent'
    COMMISSIONER        = 'commissioner',       'Commissioner'


# ─────────────────────────────────────────────────────────────
# CUSTOM USER MANAGER
# ─────────────────────────────────────────────────────────────
class OfficerUserManager(BaseUserManager):

    def create_user(self, badge_number, email, password=None, **extra_fields):
        if not badge_number:
            raise ValueError('Badge number is required')
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user  = self.model(badge_number=badge_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, badge_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role',         OfficerRole.ADMIN)
        return self.create_user(badge_number, email, password, **extra_fields)


# ─────────────────────────────────────────────────────────────
# CUSTOM USER MODEL — OfficerUser
# ─────────────────────────────────────────────────────────────
class OfficerUser(AbstractBaseUser, PermissionsMixin):

    # ── Core fields ──────────────────────────────────────────
    badge_number    = models.CharField(max_length=20,  unique=True)
    email           = models.EmailField(unique=True)
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)

    # ── Police specific fields ───────────────────────────────
    role            = models.CharField(
                        max_length=20,
                        choices=OfficerRole.choices,
                        default=OfficerRole.OFFICER
                      )
    rank            = models.CharField(
                        max_length=20,
                        choices=OfficerRank.choices,
                        default=OfficerRank.CONSTABLE
                      )
    station         = models.CharField(max_length=100, blank=True)   # e.g. Kampala Central
    district        = models.CharField(max_length=100, blank=True)   # e.g. Kampala
    phone_number    = models.CharField(max_length=15,  blank=True)
    profile_photo   = models.ImageField(
                        upload_to='officers/photos/',
                        null=True,
                        blank=True
                      )

    # ── Status fields ────────────────────────────────────────
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_verified     = models.BooleanField(default=False)   # verified by admin

    # ── Timestamps ───────────────────────────────────────────
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_updated    = models.DateTimeField(auto_now=True)

    # ── Auth config ──────────────────────────────────────────
    objects         = OfficerUserManager()
    USERNAME_FIELD  = 'badge_number'                       # login with badge number
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name        = 'Officer'
        verbose_name_plural = 'Officers'
        ordering            = ['-date_joined']

    def __str__(self):
        return f"{self.rank} {self.first_name} {self.last_name} ({self.badge_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == OfficerRole.ADMIN