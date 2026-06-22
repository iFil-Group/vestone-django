from django import template

register = template.Library()


@register.filter
def get_attr(obj, name):
    return getattr(obj, name, "")


@register.filter
def is_delete_field(field):
    return field.name.endswith("-DELETE") or field.name == "DELETE"
