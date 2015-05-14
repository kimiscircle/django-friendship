from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from friendship.contrib.suggestions.managers import FriendshipSuggestionManager

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class FriendshipSuggestion(models.Model):
    """
    A friendship suggestion connects two users that can possibly know each other.
    Suggestions can be created by somehow comparing some of user profiles fields
    (like city or address) or by importing user contacts from external services
    and then comparing names and email of imported contacts with users.
    """

    from_user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("from user"), related_name="suggestions_from")
    to_user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("to user"), related_name="suggestions_to")
    added = models.DateTimeField(_("added"), default=timezone.datetime.utcnow())

    objects = FriendshipSuggestionManager()

    class Meta:
        unique_together = [("to_user", "from_user")]
        db_table = 'friendship_friendsuggestion'


class ImportedContact(models.Model):
    """
    Contact imported from external service.
    """
    # user who imported this contact
    owner = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("owner"), related_name="imported_contacts")

    name = models.CharField(_("name"), max_length=100, null=True, blank=True)
    # Facebook does not give emails of user friends so email can be blank and
    # matching should be done using only name
    email = models.EmailField(_("email"), null=True, blank=True)

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+18012345678'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], blank=True, max_length = 16)  # validators should be a list

    added = models.DateTimeField(_("added"), default=timezone.datetime.utcnow())

    @property
    def display_name(self):
        dname = ''
        if self.email:
            dname = self.email
        if dname and self.name:
            dname += " - "
        dname += self.name
        return dname

    def __unicode__(self):
        return _("%(display_name)s (%(owner)s's contact)") % {'display_name': self.display_name, 'owner': self.owner}

    class Meta:
        db_table = 'friendship_importedcontact'
