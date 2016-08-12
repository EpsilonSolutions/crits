from django import forms
from django.forms.utils import ErrorList

from crits.campaigns.campaign import Campaign
from crits.core.forms import add_bucketlist_to_form, add_ticket_to_form, SourceInForm
from crits.core.handlers import get_item_names, get_source_names
from crits.core.user_tools import get_user_organization
from crits.core.user_tools import get_user_permissions

from crits.core import form_consts

from crits.vocabulary.relationships import RelationshipTypes


relationship_choices = [(c, c) for c in RelationshipTypes.values(sort=True)]


class AddBackdoorForm(SourceInForm):
    """
    Django form for adding a Backdoor to CRITs.
    """

    error_css_class = 'error'
    required_css_class = 'required'

    name = forms.CharField(label=form_consts.Backdoor.NAME, required=True)
    aliases = forms.CharField(label=form_consts.Backdoor.ALIASES,
                              required=False)
    version = forms.CharField(label=form_consts.Backdoor.VERSION,
                                  required=False)
    description = forms.CharField(label=form_consts.Backdoor.DESCRIPTION,
                                  required=False)
    campaign = forms.ChoiceField(widget=forms.Select,
                                 label=form_consts.Backdoor.CAMPAIGN,
                                 required=False)
    confidence = forms.ChoiceField(label=form_consts.Backdoor.CAMPAIGN_CONFIDENCE,
                                   required=False)

    related_id = forms.CharField(widget=forms.HiddenInput(), required=False, label=form_consts.Common.RELATED_ID)
    related_type = forms.CharField(widget=forms.HiddenInput(), required=False, label=form_consts.Common.RELATED_TYPE)
    relationship_type = forms.ChoiceField(required=False,
                                          label=form_consts.Common.RELATIONSHIP_TYPE,
                                          widget=forms.Select(attrs={'id':'relationship_type'}))

    def __init__(self, username, *args, **kwargs):
        super(AddBackdoorForm, self).__init__(username, *args, **kwargs)

        if get_user_permissions(username, 'Campaign')['read']:
            self.fields['campaign'].choices = [('', '')] + [
                (c.name, c.name) for c in get_item_names(Campaign, True)]
        self.fields['confidence'].choices = [
            ('', ''),
            ('low', 'low'),
            ('medium', 'medium'),
            ('high', 'high')]

        self.fields['relationship_type'].choices = relationship_choices
        self.fields['relationship_type'].initial = RelationshipTypes.RELATED_TO

        add_bucketlist_to_form(self)
        add_ticket_to_form(self)

    def clean(self):
        cleaned_data = super(AddBackdoorForm, self).clean()
        campaign = cleaned_data.get('campaign')

        if campaign:
            confidence = cleaned_data.get('confidence')

            if not confidence or confidence == '':
                self._errors.setdefault('confidence', ErrorList())
                self._errors['confidence'].append(u'This field is required if campaign is specified.')

        return cleaned_data
