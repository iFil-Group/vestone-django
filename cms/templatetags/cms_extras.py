from django import template

register = template.Library()


@register.filter
def get_attr(obj, name):
    display = getattr(obj, f"get_{name}_display", None)
    if callable(display):
        return display()
    return getattr(obj, name, "")


@register.filter
def is_delete_field(field):
    return field.name.endswith("-DELETE") or field.name == "DELETE"


@register.filter
def message_type(tags):
    tag_list = (tags or "").split()
    for name in ("error", "warning", "success", "info"):
        if name in tag_list:
            return name
    return "info"
