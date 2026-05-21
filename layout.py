# layout.py

# import yaml
# from typing import Optional, Dict
# from models import WidgetBBox, WidgetStack


# def load_widget_layout(yaml_file: str, title_map: dict[str, str]) -> Dict[str, WidgetStack]:
#     """Load the widget layout from a YAML file and build a hierarchy of WidgetStack objects."""
#     with open(yaml_file, 'r') as f:
#         layout = yaml.safe_load(f)

#     all_widgets: Dict[str, WidgetStack] = {}

#     def build_stack(name: str, data: dict, parent: Optional[WidgetStack] = None) -> WidgetStack:
#         bbox = WidgetBBox(
#             name=name,
#             width=data['width'],
#             height=data['height'],
#             Xtl=data['Xtl'],
#             Ytl=data['Ytl'],
#         )
#         window_title = title_map.get(name) if parent is None else None
#         stack = WidgetStack(bbox=bbox, parent=parent, window_title=window_title)
#         all_widgets[name] = stack

#         children = data.get('children', {})
#         # for child_name, child_data in children.items():
#         if children:        
#             for child_name, child_data in data.get('children', {}).items():
#                 build_stack(child_name, child_data, parent=stack)

#         return stack

#     for root_name, root_data in layout.items():
#         build_stack(root_name, root_data)

#     return all_widgets



# layout.py

from __future__ import annotations

from typing import Dict

from mb_tools.pseudo_widgets import WidgetStack, load_widget_stacks


def flatten_widget_stacks(
    roots: dict[str, WidgetStack],
    *,
    allow_duplicates: bool = False,
) -> dict[str, WidgetStack]:
    """
    Return a flat widget-name -> WidgetStack mapping.

    This preserves the old ToS_gui_survey calling style while using
    mb_tools.pseudo_widgets as the source of truth.
    """

    flat: dict[str, WidgetStack] = {}

    for root in roots.values():
        for node in root.iter_depth_first():
            if node.name in flat:
                if allow_duplicates:
                    continue

                raise ValueError(
                    f"Duplicate widget name {node.name!r}: "
                    f"{flat[node.name].path!r} and {node.path!r}"
                )

            flat[node.name] = node

    return flat


def load_widget_layout(
    yaml_file: str,
    title_map: dict[str, str] | None = None,
) -> Dict[str, WidgetStack]:
    """
    Load the widget layout from YAML using mb_tools.pseudo_widgets.

    The title_map argument is accepted for backward compatibility with
    the old ToS_gui_survey call site, but mb_tools.pseudo_widgets does
    not currently store window_title on the WidgetStack.
    """

    roots = load_widget_stacks(yaml_file)
    return flatten_widget_stacks(roots)
