from datetime import datetime

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings

from badges.signals import badge_awarded
from badges.managers import BadgeManager

if hasattr(settings, 'BADGE_LEVEL_CHOICES'):
    LEVEL_CHOICES = settings.BADGE_LEVEL_CHOICES
else:
    LEVEL_CHOICES = (
        ("1", "Bronze"),
        ("2", "Silver"),
        ("3", "Gold"),
        ("4", "Diamond"),
    )

class Badge(models.Model):
    id = models.CharField(max_length=255, primary_key=True)

    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    
    icon = models.ImageField(upload_to='badge_images')
    
    objects = BadgeManager()
    
    @property
    def meta_badge(self):
        from utils import registered_badges
        return registered_badges[self.id]
    
    @property
    def title(self):
        return self.meta_badge.title
    
    @property
    def description(self):
        return self.meta_badge.description
    
    def __unicode__(self):
        return u"%s" % self.title
    
    def get_absolute_url(self):
        return reverse('badge_detail', kwargs={'slug': self.id})
    
    def award_to(self, laureate):
        laureate_ctype = ContentType.objects.get_for_model(laureate)

        # Check if the laureate already has this badge
        has_badge = False

        laureate_badges = BadgeToLaureate.objects.filter(badge=self,
                                                         laureate_content_type=laureate_ctype,
                                                         laureate_object_id=laureate.pk)
        
        if laureate_badges.count():
            has_badge = True


        if self.meta_badge.one_time_only and has_badge:
            return False
        
        # Create badge
        BadgeToLaureate.objects.create(badge=self, 
                                       laureate_content_type=laureate_ctype,
                                       laureate_object_id=laureate.pk)

                
        badge_awarded.send(sender=self.meta_badge, laureate=laureate, badge=self)
        
        # message_template = "You just got the %s Badge!"
        # user.message_set.create(message = message_template % self.title)
        
        return BadgeToLaureate.objects.filter(badge=self, 
                                              laureate_content_type=laureate_ctype,
                                              laureate_object_id=laureate.pk).count()

    def number_awarded(self, candidate_or_qs=None):
        """
        Gives the number awarded total. Pass in an argument to
        get the number per user, or per queryset.
        """
        kwargs = {'badge': self}

        if isinstance(candidate_or_qs, models.query.QuerySet):
            laureate_ctype = ContentType.objects.get_for_model(candidate_or_qs.model)
            kwargs.update(dict(laureate_object_id__in=candidate_or_qs,
                               laureate_content_type=laureate_ctype))
        else:
            laureate_ctype = ContentType.objects.get_for_model(candidate_or_qs)
            kwargs.update(dict(laureate_object_id=candidate_or_qs.pk,
                               laureate_content_type=laureate_ctype))

        return BadgeToLaureate.objects.filter(**kwargs).count()


class BadgeToLaureate(models.Model):
    badge = models.ForeignKey(Badge, related_name='laureates')

    laureate_content_type = models.ForeignKey(ContentType)
    laureate_object_id = models.PositiveIntegerField()
    laureate = generic.GenericForeignKey('laureate_content_type', 'laureate_object_id')
    
    created = models.DateTimeField(default=datetime.now)

    def __unicode__(self):
        return "%s for %s (%s)" % (self.badge.meta_badge.title, self.laureate, self.laureate_content_type)
