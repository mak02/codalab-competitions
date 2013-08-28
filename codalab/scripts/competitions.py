#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
# 

import sys, os.path, os, random, datetime
from django.utils import timezone
# This is a really, really long way around saying that if the script is in
#  codalab\scripts\users.py, we need to add, ../../../codalab to the sys.path to find the settings
root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "codalab")
sys.path.append(root_dir)

# Set things for django configurations
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "codalab.settings")

# Import the configuration
from configurations import importer
importer.install()

from django.core.files import File
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.web.models import *

# Get the user model
User = get_user_model()

# Deal with time
start_date = timezone.now()

# Get a user to be the creator
guest1 = User.objects.get(username="guest1")

#
#  Start BRaTS 2012 ----
#

# BRaTS 2012
brats12_name = "MICCAI Multimodal Brain Tumor Segmentation (BRaTS) Challenge 2012"
brats12_description = """
        The BRaTS challenge is designed to gauge the current state-of-the-art in automated brain tumor segmentation 
        and to compare between different methods. It is organized in conjuction with the MICCAI 2012 conference.
        """
brats2012,_ = Competition.objects.get_or_create(title=brats12_name, creator=guest1, modified_by=guest1,defaults=dict(description=brats12_description))
details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc,_ = PageContainer.objects.get_or_create(object_id=brats2012.id, content_type=ContentType.objects.get_for_model(Competition))
brats2012.pagecontent = pc
brats2012.save()

Page.objects.get_or_create(category=details_category, container=pc,  codename="overview",
                           defaults=dict(label="Overview", rank=0,
                                         html=open(os.path.join(os.path.dirname(__file__), "brats2012_overview.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="evaluation", 
                           defaults=dict(label="Evaluation", rank=1,
                                         html=open(os.path.join(os.path.dirname(__file__), "brats2012_evaluation.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="terms_and_conditions",
                    defaults=dict(rank=2, label="Terms and Conditions", html=open(os.path.join(os.path.dirname(__file__), "brats2012_terms_and_conditions.html")).read()))

Page.objects.get_or_create(category=details_category, container=pc,  codename="faq",
                           defaults=dict(label="FAQ", rank=3, html=open(os.path.join(os.path.dirname(__file__), "brats2012_faq.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="key_dates",
                           defaults=dict(label="Key Dates", rank=4, html=open(os.path.join(os.path.dirname(__file__), "brats2012_key_dates.html")).read()))
Page.objects.get_or_create(category=details_category, container=pc,  codename="organizers",
                           defaults=dict(label="Organizers", rank=5,html=open(os.path.join(os.path.dirname(__file__), "brats2012_organizers.html")).read()))

Page.objects.get_or_create(category=participate_category, container=pc,  codename="get_data",
                    defaults=dict(label="Get Data", rank=0, html=open(os.path.join(os.path.dirname(__file__), "brats2012_data.html")).read()))
Page.objects.get_or_create(category=participate_category, container=pc,  codename="submit_results", html="", defaults=dict(label="Submit Results", rank=1))

# Logo
brats2012.image = File( open(os.path.join(root_dir, "fixtures", "images", "brats.jpg"), 'rb'))

# Save the updates
brats2012.save()


                        

# Phases for the competition
day_delta = datetime.timedelta(days=30)
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 7, 6), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2012, 10, 1), datetime.time()), timezone.get_current_timezone())
p1date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 7, 15), datetime.time()), timezone.get_current_timezone())
p2date = timezone.make_aware(datetime.datetime.combine(datetime.date(2013, 8, 30), datetime.time()), timezone.get_current_timezone())
p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=1, label="Training Phase",
                                                                                                        start_date=p1date, max_submissions=100)
p, created = CompetitionPhase.objects.get_or_create(competition=brats2012, phasenumber=2, label="Competition Phase",
                                                                                                        start_date=p2date, max_submissions=1)

## Score Definitions


groups = {}
for g in ({'key': 'patient', 'label': 'Patient Data'},
          {'key': 'synthetic', 'label': 'Synthetic Data'},
          ):
        rg,cr = SubmissionResultGroup.objects.get_or_create(competition=brats2012,
                                                            key=g['key'],
                                                            defaults=dict(label=g['label']))
        groups[rg.key] = rg

for sdg in ( 
        ('synthetic',({'Dice': {'subs': (('SyntheticDiceComplete','Complete'),('SyntheticDiceCore','Core'))  } },
                      {'Sensitivity': {'subs': (('SyntheticSensitivityComplete','Complete'),('SyntheticSensitivityCore','Core'))  }},
                      {'Specificity': {'subs': (('SyntheticSpecificityComplete','Complete'),('SyntheticSpecificityCore','Core')) }},
                      {'Hausdorff': {'subs': (('SyntheticHausdorffComplete','Complete'),('SyntheticHausdorffCore','Core'))}},
                      {'Kappa': {'def':  ('SyntheticKappa','Kappa')}},
                      {'Rank': { 'computed': {'operation': 'Avg', 'key': 'synthetic_dice_rank', 'label': 'Rank', 'fields': ('SyntheticDiceComplete','SyntheticDiceCore')}}}) 
         ) ,

        ('patient',({'Dice': {'subs': (('PatientDiceComplete','Complete'),('PatientDiceCore','Core'),('PatientDiceEnhancing','Enhancing'))  } },
                    {'Sensitivity': {'subs': (('PatientSensitivityComplete','Complete'),('PatientSensitivityCore','Core'),('PatientSensitivityEnhancing','Enhancing'))  }},
                    {'Specificity': {'subs': (('PatientSpecificiyComplete','Complete'),('PatientSpecificiyCore','Core'),('PatientSpecificiyEnhancing','Enhancing')) }},
                    {'Hausdorff': {'subs': (('PatientHausdorffComplete','Complete'),('PatientHausdorffCore','Core'),('PatientHausdorffEnhancing','Enhancing'))}},
                    {'Kappa': {'def':  ('PatientKappa','Kappa')}},
                    {'Rank': { 'computed': {'operation': 'Avg', 'key': 'patient_dice_rank', 'label': 'Rank', 'fields': ('PatientDiceComplete','PatientDiceCore','PatientDiceEnhancing')}}})  ),
           ):
        

        rgroup,sg = sdg
        print "RGROUP", rgroup
        comp = []
        fields = {}
        for s in sg: 
                for label,e in s.items():
                        print "E",e
                        
                        for t,defs in e.items():
                                print "DEFS",defs
                                
                                if t == 'computed':
                                        g,cr = SubmissionScoreGroup.objects.get_or_create(key=defs['key'],competition=brats2012, defaults=dict(label=label))
                                        comp.append((label,defs,g))
                                        print "COMPUTED"
                                elif t == 'subs':
                                        g,cr = SubmissionScoreGroup.objects.get_or_create(key="%s%s" % (rgroup,label),
                                                                                          competition=brats2012, defaults=dict(label=label))
                                        for sub in defs:
                                                print "SUB",sub
                                                

                                                sd,cr = SubmissionScoreDef.objects.get_or_create(group=groups[rgroup],key=sub[0],
                                                                                                        defaults=dict(label=sub[1]))
                                                fields[sd.key] = sd

                                                print " CREATED DEF", sd.key, sd.label
                                                for p in brats2012.phases.all():
                                                        sp,cr = SubmissionScorePhase.objects.get_or_create(scoredef=sd,phase=p)
                                                        print "   ADDED TO PHASE"

                                                g2,cr = SubmissionScoreGroup.objects.get_or_create(parent=g,
                                                                                                   key=sub[0],
                                                                                                   competition=brats2012,
                                                                                                   defaults=dict(scoredef=sd,label=sub[1]))
                                                print " SUB GROUP", g2.label,g2.scoredef.key,g2.scoredef.label

                                elif t == 'def':
                                        g,cr = SubmissionScoreGroup.objects.get_or_create(key="%s%s" % (rgroup,label),
                                                                                          competition=brats2012, defaults=dict(label=defs[1]))
                                        sd,cr = SubmissionScoreDef.objects.get_or_create(group=groups[rgroup],
                                                                                         key=defs[0],
                                                                                         defaults = dict(label=defs[1]))
                                        fields[sd.key] = sd

                                        for p in brats2012.phases.all():
                                                sp,cr = SubmissionScorePhase.objects.get_or_create(scoredef=sd,phase=p)
                                        g.scoredef = sd
                                        g.save()
        for label,defs,g in comp:
                sd,cr = SubmissionScoreDef.objects.get_or_create(group=groups[rgroup],
                                                                 key=defs['key'],
                                                                 defaults=dict(label=defs['label']),
                                                                 computed=True)
                for p in brats2012.phases.all():
                        SubmissionScorePhase.objects.get_or_create(scoredef=sd,phase=p)
                sc,cr = SubmissionComputedScore.objects.get_or_create(scoredef = sd,
                                                                      operation = defs['operation'])
                for f in defs['fields']:
                        SubmissionComputedScoreField.objects.get_or_create(computed=sc,
                                                                           scoredef=fields[f])
                g.scoredef = sd
                g.save()
# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()

# Participants for the competition
participants = [ (statuses[i-2], User.objects.get(username="guest%d" % i)) for i in range(2,len(statuses)+2)]

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()

# Add participants to the competition with random statuses
for status, participant in participants:
        print "Adding %s to competition %s with status %s" % (participant, brats2012, status)
        resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=brats2012, 
                                                                                                                                                                  defaults={'status':status})
#
#  End BRaTS 2012 ----
#

# Spine Localization
spine_name = "Spine Localization Example"
spine_description = """
        Test for server side execution of evaluation program.
"""
spine,created = Competition.objects.get_or_create(title=spine_name, creator=guest1, modified_by=guest1, 
                                                                                                  description=spine_description, has_registration=True)

details_category = ContentCategory.objects.get(name="Learn the Details")
participate_category = ContentCategory.objects.get(name="Participate")
pc,_ = PageContainer.objects.get_or_create(object_id=spine.id, content_type=ContentType.objects.get_for_model(Competition))
spine.pagecontent = pc
spine.save()

# Page.objects.get_or_create(category=details_category, container=pc,  codename="overview",
#                                       defaults=dict(label="Overview", rank=0,
#                                        html=open(os.path.join(os.path.dirname(__file__), "example_overview.html")).read()))
# Page.objects.get_or_create(category=details_category, container=pc,  codename="evaluation", 
#                                       defaults=dict(label="Evaluation", rank=1,
#                                        html=open(os.path.join(os.path.dirname(__file__), "example_evaluation.html")).read()))
# Page.objects.get_or_create(category=details_category, container=pc,  codename="terms_and_conditions",
#                     defaults=dict(rank=2, label="Terms and Conditions", html=open(os.path.join(os.path.dirname(__file__), "example_terms_and_conditions.html")).read()))
# Page.objects.get_or_create(category=participate_category, container=pc,  codename="get_data",
#                     defaults=dict(label="Get Data", rank=0, html=open(os.path.join(os.path.dirname(__file__), "example_data.html")).read()))
# Page.objects.get_or_create(category=participate_category, container=pc,  codename="submit_results", html="", defaults=dict(label="Submit Results", rank=1))

# Logo
spine.image = File(open(os.path.join(root_dir, "fixtures", "images", "spine.jpg"), 'rb'))

# Save updates
spine.save()

# Phases for the competition
day_delta = datetime.timedelta(days=30)
for phase in [1, 2]:
        phase_start = start_date + (day_delta * phase)
        p, created = CompetitionPhase.objects.get_or_create(competition=spine, phasenumber=phase, label="Phase %d" % phase,
                                                                                                                start_date=phase_start, max_submissions=4)

# Participants for the competition
participants = [ User.objects.get(username="guest%d" % random.choice(range(1,10))) for i in range(random.choice(range(1, 5)))]
# print participants

# Participant statuses, if they haven't been created before
statuses = ParticipantStatus.objects.all()
# print statuses

# Add participants to the competition with random statuses
for participant in participants:
        status = random.choice(statuses)
        # print "Adding %s to competition %s with status %s" % (participant, spine, status)
        resulting_participant, created = CompetitionParticipant.objects.get_or_create(user=participant, competition=spine, 
                                                                                                                                                                  defaults={'status':status})
#
#  End Spine Localization ----
#

exit(0)

import random
phase = CompetitionPhase.objects.all()[0]
participant = CompetitionParticipant.objects.all()[0]
participant2 = CompetitionParticipant.objects.all()[2]
submission = CompetitionSubmission.objects.get_or_create(participant=participant,phase=phase)[0]
submission2 = CompetitionSubmission.objects.get_or_create(participant=participant2,phase=phase)[0]
result = SubmissionResult.objects.get_or_create(submission=submission,name='Test1',aggregate=0.0)[0]
result2 = SubmissionResult.objects.get_or_create(submission=submission2,name='Test2',aggregate=0.0)[0]
for s in SubmissionScoreDef.objects.filter(computed=False):
    score = SubmissionScore.objects.get_or_create(scoredef=s,result=result,defaults=(dict(value=random.random())))
    score = SubmissionScore.objects.get_or_create(scoredef=s,result=result2,defaults=(dict(value=random.random())))


from django.db import models as djmodels


LABELS = {}
VALUES = {}
CUR={}
SCORES={}
for x in SubmissionScoreGroup.objects.order_by('tree_id','lft').filter(scoredef__isnull=False,  scoredef__phases__in=[phase]):
        label = x.label
	group_key = x.scoredef.group.key
	group_label = x.scoredef.group.label

        if x.scoredef.computed is True: 
                COMP_KEYS = [cf.scoredef.key for cf in x.scoredef.computed_score.fields.all()]
                if not COMP_KEYS:
                        continue

        if x.parent is not None:
                label_key = x.parent.label
                d = [label]
        else:
                label_key = label
                d = []
	if group_key not in LABELS:
		LABELS[group_key] = { 'label':group_label, 'values':[] }
	if group_key not in CUR:
		CUR[group_key] = { }
        if label_key not in CUR[group_key]:
                CUR[group_key][label_key] = {label_key:[]}
                LABELS[group_key]['values'].append(CUR[group_key][label_key])
        CUR[group_key][label_key][label_key].extend(d)

        if x.scoredef.computed is True:
                AGG_OP = getattr(djmodels,x.scoredef.computed_score.operation)
                for s in SubmissionScore.objects.filter(scoredef__key__in=COMP_KEYS,scoredef__phases__in=[phase]).values('result__pk').annotate(value=AGG_OP('value')):
                        pk = s['result__pk']
			if group_key not in SCORES:
				SCORES[group_key] = {}
                        if pk not in SCORES[group_key]:
                                SCORES[group_key][pk] = { 'username': SubmissionResult.objects.get(pk=pk).participant.user.username,
							  'scores': []}
                        SCORES[group_key][pk]['scores'].append(dict(value=s['value'],key=x.scoredef.key))
                                
        else:
                for s in x.scoredef.submissionscore_set.order_by('result__pk').all():
			if group_key not in SCORES:
				SCORES[group_key] = {}
                        if s.result.pk not in SCORES[group_key]:
                                SCORES[group_key][s.result.pk] = { 'username': s.result.submission.participant.user.username,
                                                        'scores': []}
                        SCORES[group_key][s.result.pk]['scores'].append(dict(value=s.value,key=s.scoredef.key))
print LABELS
print SCORES
