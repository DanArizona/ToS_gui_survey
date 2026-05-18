# layout.py

import yaml
from typing import Optional, Dict
from models import WidgetBBox, WidgetStack


def load_widget_layout(yaml_file: str, title_map: dict[str, str]) -> Dict[str, WidgetStack]:
    """Load the widget layout from a YAML file and build a hierarchy of WidgetStack objects."""
    with open(yaml_file, 'r') as f:
        layout = yaml.safe_load(f)

    all_widgets: Dict[str, WidgetStack] = {}

    def build_stack(name: str, data: dict, parent: Optional[WidgetStack] = None) -> WidgetStack:
        bbox = WidgetBBox(
            name=name,
            width=data['width'],
            height=data['height'],
            Xtl=data['Xtl'],
            Ytl=data['Ytl'],
        )
        window_title = title_map.get(name) if parent is None else None
        stack = WidgetStack(bbox=bbox, parent=parent, window_title=window_title)
        all_widgets[name] = stack

        children = data.get('children', {})
        # for child_name, child_data in children.items():
        if children:        
            for child_name, child_data in data.get('children', {}).items():
                build_stack(child_name, child_data, parent=stack)

        return stack

    for root_name, root_data in layout.items():
        build_stack(root_name, root_data)

    return all_widgets
