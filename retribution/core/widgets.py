from django import forms


class AjaxTypeaheadWidget(forms.TextInput):
    def __init__(self, url, data_type='typeahead-ajax', attrs=None, *args, **kwargs):
        """
        A custom widget that adds a "customer" data-type so it gets
        autocompleted by Typeahead.js
        """
        widget_attrs = {
            'autocomplete': 'off',
            'data-type': data_type,
            'data-typeahead-url': url,
        }
        if attrs is not None:
            widget_attrs.update(attrs)
        super(AjaxTypeaheadWidget, self).__init__(*args, attrs=widget_attrs, **kwargs)
