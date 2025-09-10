""" This module is a form to parse multiple Manager Ids on the Manager
page. """

from django import forms

from fpl.dataloader.load.load_managers import check_manager_exists
from fpl.exceptions.manager_exceptions import ManagerNotFoundError
from fpl.properties.properties import get_properties

properties = get_properties()


class ManagerIdForm(forms.Form):
    """ Form use on the manager page to allow entry of multiple ids for team
    comparison """

    error_css_class = "custom_error"
    manager_ids = forms.CharField(label="Manager ids ",
                                  initial=properties.manager_ids)

    def clean(self):
        """ Function to parse multiple manager ids """
        data = self.cleaned_data.get('manager_ids')
        manager_ids = [int(x) for x in data.split(',')]
        for manager_id in manager_ids:
            try:
                check_manager_exists(manager_id)
            except ManagerNotFoundError as exc:
                raise forms.ValidationError(f"Manager {manager_id} does not "
                                            f"exist") from exc
        return data
