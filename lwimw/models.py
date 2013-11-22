from django.db import models
from django.db.models import Sum, Avg
from django.contrib.auth.models import *
from django.utils import timezone
from util.functions import *
import re
import ipdb
from datetime import date, timedelta


class ContestManager(models.Manager):
    pass


class Contest(models.Model):
    number = models.PositiveIntegerField(unique=True)
    theme = models.CharField(max_length=255)
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    objects = ContestManager()

    def __unicode__(self):
        return 'Look What I Made Weekend %d - %s' % (self.number, self.theme)

    def get_current_state(self):
        now = timezone.now()
        return self.get_contest_state(now)

    def get_contest_state(self, now):
        if now.year < self.year or now.year == self.year and now.month < self.month:
            return 'before'
        elif now.year == self.year and now.month == self.month:
            return 'during'
        elif (now.year == self.year and now.month == self.month + 1 or 
              now.year == self.year + 1 and now.month == 1):
            return 'judging'
        else:
            return 'after'

    def get_results(self):

        return (self.submissions.all().
            annotate(avg_innovation=Avg('ratings__innovation')).
            annotate(avg_theme=Avg('ratings__theme')).
            annotate(avg_refinement=Avg('ratings__refinement')).
            annotate(avg_artistry=Avg('ratings__artistry')).
            annotate(avg_overall=Avg('ratings__overall')).
            order_by('-avg_overall')
        )

    def get_long_month_name(self):
        return [
            'Negative',
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December',
        ][self.month]

    def get_short_month_name(self):
        return [
            'Neg',
            'Jan',
            'Feb',
            'Mar',
            'Apr',
            'May',
            'Jun',
            'Jul',
            'Aug',
            'Sep',
            'Oct',
            'Nov',
            'Dec',
        ][self.month]


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'



class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
    contest = models.ForeignKey(Contest, related_name='submissions')
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='submissions')
    comments = models.TextField(blank=True)
    link_1 = models.CharField("Link 1 (Optional)", max_length=255, blank=True, null=True)
    link_2 = models.CharField("Link 2 (Optional)", max_length=255, blank=True, null=True)
    link_3 = models.CharField("Link 3 (Optional)", max_length=255, blank=True, null=True)
    image_1 = models.ImageField("Image 1 (Optional)", upload_to='submission_images', blank=True, null=True)
    image_2 = models.ImageField("Image 2 (Optional)", upload_to='submission_images', blank=True, null=True)
    image_3 = models.ImageField("Image 3 (Optional)", upload_to='submission_images', blank=True, null=True)
    receive_ratings = models.BooleanField('Allow others to rate my entry', default=True)
    used_theme = models.BooleanField('I used the theme', default=True)


class Rating(models.Model):
    RATINGS = (
        (0, 'Not Applicable'),
        (1, 'One Star'),
        (2, 'Two Stars'),
        (3, 'Three Stars'),
        (4, 'Four Stars'),
        (5, 'Five Stars'),
    )
    rater = models.ForeignKey(User, related_name='ratings')
    submission = models.ForeignKey(Submission, related_name='ratings')

    innovation = models.PositiveIntegerField(choices=RATINGS)
    theme = models.PositiveIntegerField(choices=RATINGS)
    refinement = models.PositiveIntegerField(choices=RATINGS)
    artistry = models.PositiveIntegerField(choices=RATINGS)
    overall = models.PositiveIntegerField(choices=RATINGS)
    comments = models.TextField(blank=True)


class Post(models.Model):
    author = models.ForeignKey(User, related_name='posts')
    contest = models.ForeignKey(Contest, related_name='posts')
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    image = models.ImageField('Image (Optional)', upload_to='post_images', blank=True, null=True)

