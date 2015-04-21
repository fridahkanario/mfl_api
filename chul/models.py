from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from common.models import AbstractBase, Contact, SequenceMixin, Ward
from common.fields import SequenceField
from facilities.models import Facility


class Status(AbstractBase):
    """
    Indicates the of operation of a community health unit.
    e.g  fully-functional, semi-functional, functional
    """
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class Approver(AbstractBase):
    """
    These are the bodies or the people that approve a community health unit.
    """
    name = models.CharField(
        max_length=150, help_text='name of the approver', unique=True)
    description = models.TextField(null=True, blank=True)
    abbreviation = models.CharField(
        max_length=50, help_text='A short name for the approver.')

    def __unicode__(self):
        return self.name


class ApprovalStatus(AbstractBase):
    """
    Status of a community health unit indicatting whether it has been
    approved or not.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class Community(SequenceMixin, AbstractBase):
    """
    A certain area within a ward.
    """
    name = models.CharField(max_length=100)
    code = SequenceField(unique=True)
    ward = models.ForeignKey(Ward)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_next_code_sequence()
        super(Community, self).save(*args, **kwargs)


class CommunityHealthUnitContact(AbstractBase):
    """
    The contacts of the health unit may be email, fax mobile etc.
    """
    health_unit = models.ForeignKey('CommunityHealthUnit')
    contact = models.ForeignKey(Contact)

    def __unicode__(self):
        return "{}: {}".format(self.health_unit, self.contact)


class CommunityHealthUnit(SequenceMixin, AbstractBase):
    """
    This is a health service delivery structure within a defined geographical
    area covering a population of approximately 5,000 people.

    Each unit is assigned 2 Community Health Extension Workers (CHEWs) and
    community health volunteers who offer promotive, preventative and basic
    curative health services
    """
    name = models.CharField(max_length=100)
    code = SequenceField(unique=True)
    facility = models.ForeignKey(
        Facility,
        help_text='The facility on which the health unit is tied to.')
    status = models.ForeignKey(Status)
    community = models.ForeignKey(
        Community,
        help_text='Community area within which the health unit is located')
    households_monitored = models.PositiveIntegerField(default=0)
    date_established = models.DateField(default=timezone.now)
    contacts = models.ManyToManyField(
        Contact, through=CommunityHealthUnitContact)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_next_code_sequence()
        super(CommunityHealthUnit, self).save(*args, **kwargs)


class EntityApprovalAbstractBase(AbstractBase):
    """
    Links an entity to its approver.
    """
    approver = models.ForeignKey(Approver)
    approval_status = models.ForeignKey(ApprovalStatus)
    comment = models.TextField()
    approval_date = models.DateField(default=timezone.now)

    class Meta:
        abstract = True


class CommunityHealthUnitApproval(EntityApprovalAbstractBase):
    """
    Links a community health unit to its approver.
    """
    health_unit = models.ForeignKey(
        CommunityHealthUnit,
        related_name='health_unit_approvals')

    def __unicode__(self):
        return "{}: {}: {}".format(
            self.approver, self.approval_status, self.health_unit)


class CommunityHealthWorkerContact(AbstractBase):
    """
    The contacts of the healh worker.

    They may be as many as the health worker has.
    """
    health_worker = models.ForeignKey('CommunityHealthWorker')
    contact = models.ForeignKey(Contact)

    def __unicode__(self):
        return "{}: {}".format(self.health_worker, self.contact)


class CommunityHealthWorker(AbstractBase):
    """
    A person who is incharge of a certain community health area.

    The status of the worker that is whether still active or not will be
    shown by the active field inherited from abstract base.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    id_number = models.PositiveIntegerField(unique=True)
    health_unit = models.ForeignKey(
        CommunityHealthUnit,
        help_text='The health unit the worker is incharge of',
        related_name='health_unit_workers')
    contacts = models.ManyToManyField(
        Contact, through=CommunityHealthWorkerContact)

    def __unicode__(self):
        return str(self.id_number)

    def validate_id_number(self):
        id_number_size = len(str(self.id_number))
        if id_number_size < 7:
            raise ValidationError("The id number given is too small.")

    class Meta:
        unique_together = ('id_number', 'health_unit')


class CommunityHealthWorkerApproval(EntityApprovalAbstractBase):
    """
    Shows wen a health worker was approved and by who.
    """
    health_worker = models.ForeignKey(
        CommunityHealthWorker, related_name='health_worker_approvals')

    def __unicode__(self):
        return "{}: {}: {}".format(
            self.approver, self.approval_status, self.health_worker)
