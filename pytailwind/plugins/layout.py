"""
Layout utility plugins.

Includes: display, position, flex, grid, visibility, z-index, etc.
"""

from typing import List, Optional, Dict
from .base import UtilityPlugin, SimpleUtilityPlugin, GeneratorContext
from ..parser import TailwindToken, ValueType
from ..ast import Rule


class DisplayPlugin(UtilityPlugin):
    """Plugin for display utilities (block, flex, grid, hidden, etc.)."""
    
    name = "display"
    prefixes = [
        "block", "inline", "inline-block", "flex", "inline-flex",
        "grid", "inline-grid", "table", "inline-table", "table-row",
        "table-cell", "hidden", "contents", "flow-root", "list-item"
    ]
    
    STATIC_VALUES = {
        'block': 'block',
        'inline': 'inline',
        'inline-block': 'inline-block',
        'flex': 'flex',
        'inline-flex': 'inline-flex',
        'grid': 'grid',
        'inline-grid': 'inline-grid',
        'table': 'table',
        'inline-table': 'inline-table',
        'table-row': 'table-row',
        'table-cell': 'table-cell',
        'table-caption': 'table-caption',
        'table-column': 'table-column',
        'table-column-group': 'table-column-group',
        'table-footer-group': 'table-footer-group',
        'table-header-group': 'table-header-group',
        'table-row-group': 'table-row-group',
        'hidden': 'none',
        'contents': 'contents',
        'flow-root': 'flow-root',
        'list-item': 'list-item',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        # Match single-word utilities that equal the utility
        full = token.raw.split(':')[-1]  # Get the non-variant part
        return full in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        if full in self.STATIC_VALUES:
            return self.create_rule(token, 'display', self.STATIC_VALUES[full])
        return None


class PositionPlugin(UtilityPlugin):
    """Plugin for position utilities (static, fixed, absolute, relative, sticky)."""
    
    name = "position"
    prefixes = ["static", "fixed", "absolute", "relative", "sticky"]
    
    STATIC_VALUES = {
        'static': 'static',
        'fixed': 'fixed',
        'absolute': 'absolute',
        'relative': 'relative',
        'sticky': 'sticky',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]
        return full in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        if full in self.STATIC_VALUES:
            return self.create_rule(token, 'position', self.STATIC_VALUES[full])
        return None


class ZIndexPlugin(UtilityPlugin):
    """Plugin for z-index utilities (z-*)."""
    
    name = "z-index"
    prefixes = ["z"]
    
    STATIC_VALUES = {
        '0': '0',
        '10': '10',
        '20': '20',
        '30': '30',
        '40': '40',
        '50': '50',
        'auto': 'auto',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    @property
    def supports_negative(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'z'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'z-index', value)


class FlexPlugin(UtilityPlugin):
    """Plugin for flex shorthand utilities (flex-1, flex-auto, flex-initial, flex-none)."""
    
    name = "flex-shorthand"
    prefixes = ["flex"]
    
    STATIC_VALUES = {
        '1': '1 1 0%',
        'auto': '1 1 auto',
        'initial': '0 1 auto',
        'none': 'none',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'flex':
            return False
        # Don't match flex-row, flex-col, flex-wrap, etc.
        if token.value in ('row', 'row-reverse', 'col', 'col-reverse',
                           'wrap', 'wrap-reverse', 'nowrap'):
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'flex', value)


class FlexDirectionPlugin(UtilityPlugin):
    """Plugin for flex direction utilities (flex-row, flex-col, etc.)."""
    
    name = "flex-direction"
    prefixes = ["flex"]
    
    STATIC_VALUES = {
        'row': 'row',
        'row-reverse': 'row-reverse',
        'col': 'column',
        'col-reverse': 'column-reverse',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'flex':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'flex-direction', self.STATIC_VALUES[token.value])
        return None


class FlexWrapPlugin(UtilityPlugin):
    """Plugin for flex wrap utilities (flex-wrap, flex-nowrap, etc.)."""
    
    name = "flex-wrap"
    prefixes = ["flex"]
    
    STATIC_VALUES = {
        'wrap': 'wrap',
        'wrap-reverse': 'wrap-reverse',
        'nowrap': 'nowrap',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'flex':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'flex-wrap', self.STATIC_VALUES[token.value])
        return None


class FlexGrowPlugin(UtilityPlugin):
    """Plugin for flex-grow utilities (grow, grow-0)."""
    
    name = "flex-grow"
    prefixes = ["grow"]
    
    STATIC_VALUES = {
        '': '1',  # Just "grow"
        '0': '0',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'grow'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None and not token.value:
            value = '1'  # Default for just "grow"
        if value is None:
            return None
        return self.create_rule(token, 'flex-grow', value)


class FlexShrinkPlugin(UtilityPlugin):
    """Plugin for flex-shrink utilities (shrink, shrink-0)."""
    
    name = "flex-shrink"
    prefixes = ["shrink"]
    
    STATIC_VALUES = {
        '': '1',  # Just "shrink"
        '0': '0',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'shrink'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None and not token.value:
            value = '1'  # Default for just "shrink"
        if value is None:
            return None
        return self.create_rule(token, 'flex-shrink', value)


class FlexBasisPlugin(UtilityPlugin):
    """Plugin for flex-basis utilities (basis-*)."""
    
    name = "flex-basis"
    prefixes = ["basis"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'full': '100%',
        '1/2': '50%',
        '1/3': '33.333333%',
        '2/3': '66.666667%',
        '1/4': '25%',
        '2/4': '50%',
        '3/4': '75%',
        '1/5': '20%',
        '2/5': '40%',
        '3/5': '60%',
        '4/5': '80%',
        '1/6': '16.666667%',
        '5/6': '83.333333%',
        '1/12': '8.333333%',
        '11/12': '91.666667%',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_spacing(self) -> bool:
        return True
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'basis'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'flex-basis', value)


class JustifyContentPlugin(UtilityPlugin):
    """Plugin for justify-content utilities (justify-*)."""
    
    name = "justify-content"
    prefixes = ["justify"]
    
    STATIC_VALUES = {
        'normal': 'normal',
        'start': 'flex-start',
        'end': 'flex-end',
        'center': 'center',
        'between': 'space-between',
        'around': 'space-around',
        'evenly': 'space-evenly',
        'stretch': 'stretch',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'justify':
            return False
        # Don't match justify-items-* or justify-self-*
        return token.modifier is None
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'justify-content', self.STATIC_VALUES[token.value])
        return None


class AlignItemsPlugin(UtilityPlugin):
    """Plugin for align-items utilities (items-*)."""
    
    name = "align-items"
    prefixes = ["items"]
    
    STATIC_VALUES = {
        'start': 'flex-start',
        'end': 'flex-end',
        'center': 'center',
        'baseline': 'baseline',
        'stretch': 'stretch',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'items'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'align-items', self.STATIC_VALUES[token.value])
        return None


class AlignContentPlugin(UtilityPlugin):
    """Plugin for align-content utilities (content-*)."""
    
    name = "align-content"
    prefixes = ["content"]
    
    STATIC_VALUES = {
        'normal': 'normal',
        'start': 'flex-start',
        'end': 'flex-end',
        'center': 'center',
        'between': 'space-between',
        'around': 'space-around',
        'evenly': 'space-evenly',
        'baseline': 'baseline',
        'stretch': 'stretch',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'content':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'align-content', self.STATIC_VALUES[token.value])
        return None


class AlignSelfPlugin(UtilityPlugin):
    """Plugin for align-self utilities (self-*)."""
    
    name = "align-self"
    prefixes = ["self"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'start': 'flex-start',
        'end': 'flex-end',
        'center': 'center',
        'stretch': 'stretch',
        'baseline': 'baseline',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'self'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'align-self', self.STATIC_VALUES[token.value])
        return None


class GridColumnsPlugin(UtilityPlugin):
    """Plugin for grid-template-columns utilities (grid-cols-*)."""
    
    name = "grid-template-columns"
    prefixes = ["grid-cols"]
    
    STATIC_VALUES = {
        'none': 'none',
        'subgrid': 'subgrid',
    }
    
    # Generate repeat patterns for 1-12 columns
    for i in range(1, 13):
        STATIC_VALUES[str(i)] = f'repeat({i}, minmax(0, 1fr))'
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'grid-cols'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'grid-template-columns', value)


class GridRowsPlugin(UtilityPlugin):
    """Plugin for grid-template-rows utilities (grid-rows-*)."""
    
    name = "grid-template-rows"
    prefixes = ["grid-rows"]
    
    STATIC_VALUES = {
        'none': 'none',
        'subgrid': 'subgrid',
    }
    
    # Generate repeat patterns for 1-12 rows
    for i in range(1, 13):
        STATIC_VALUES[str(i)] = f'repeat({i}, minmax(0, 1fr))'
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'grid-rows'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'grid-template-rows', value)


class OverflowPlugin(UtilityPlugin):
    """Plugin for overflow utilities (overflow-*)."""
    
    name = "overflow"
    prefixes = ["overflow"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'hidden': 'hidden',
        'clip': 'clip',
        'visible': 'visible',
        'scroll': 'scroll',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'overflow':
            return False
        return token.modifier in (None, 'x', 'y')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value not in self.STATIC_VALUES:
            return None
        
        value = self.STATIC_VALUES[token.value]
        
        if token.modifier == 'x':
            return self.create_rule(token, 'overflow-x', value)
        elif token.modifier == 'y':
            return self.create_rule(token, 'overflow-y', value)
        else:
            return self.create_rule(token, 'overflow', value)


class OrderPlugin(UtilityPlugin):
    """Plugin for order utilities (order-*)."""
    
    name = "order"
    prefixes = ["order"]
    
    STATIC_VALUES = {
        'first': '-9999',
        'last': '9999',
        'none': '0',
    }
    
    # Generate numeric orders 1-12
    for i in range(1, 13):
        STATIC_VALUES[str(i)] = str(i)
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    @property
    def supports_negative(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'order'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'order', value)


class AspectRatioPlugin(UtilityPlugin):
    """Plugin for aspect-ratio utilities (aspect-*)."""
    
    name = "aspect-ratio"
    prefixes = ["aspect"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'square': '1 / 1',
        'video': '16 / 9',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'aspect'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'aspect-ratio', value)


class ColumnsPlugin(UtilityPlugin):
    """Plugin for columns utilities (columns-*)."""
    
    name = "columns"
    prefixes = ["columns"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        '3xs': '16rem',
        '2xs': '18rem',
        'xs': '20rem',
        'sm': '24rem',
        'md': '28rem',
        'lg': '32rem',
        'xl': '36rem',
        '2xl': '42rem',
        '3xl': '48rem',
        '4xl': '56rem',
        '5xl': '64rem',
        '6xl': '72rem',
        '7xl': '80rem',
    }
    
    # Generate numeric columns 1-12
    for i in range(1, 13):
        STATIC_VALUES[str(i)] = str(i)
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'columns'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'columns', value)


class ObjectFitPlugin(UtilityPlugin):
    """Plugin for object-fit utilities (object-*)."""
    
    name = "object-fit"
    prefixes = ["object"]
    
    STATIC_VALUES = {
        'contain': 'contain',
        'cover': 'cover',
        'fill': 'fill',
        'none': 'none',
        'scale-down': 'scale-down',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'object':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'object-fit', self.STATIC_VALUES[token.value])
        return None


class ContainerPlugin(UtilityPlugin):
    """
    Plugin for container query utilities (@container).
    
    Marks an element as a container for container queries.
    Supports named containers: @container/main
    """
    
    name = "container"
    prefixes = ["@container"]
    
    def match(self, token: TailwindToken) -> bool:
        full = token.raw.split(':')[-1]  # Get the non-variant part
        return full == '@container' or full.startswith('@container/')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        full = token.raw.split(':')[-1]
        
        # Check for named container: @container/name
        if '/' in full:
            name = full.split('/')[1]
            return self.create_rule(token, 'container-name', name)
        
        # Default @container - just enable container-type
        return self.create_rule(token, 'container-type', 'inline-size')


class ContainerTypePlugin(UtilityPlugin):
    """Plugin for container-type utilities."""
    
    name = "container-type"
    prefixes = ["container"]
    
    STATIC_VALUES = {
        'normal': 'normal',
        'size': 'size',
        'inline-size': 'inline-size',
    }
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'container':
            return False
        return token.value in self.STATIC_VALUES
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value in self.STATIC_VALUES:
            return self.create_rule(token, 'container-type', self.STATIC_VALUES[token.value])
        return None


def get_plugins() -> List[UtilityPlugin]:
    """Get all layout-related plugins."""
    return [
        DisplayPlugin(),
        PositionPlugin(),
        ZIndexPlugin(),
        FlexPlugin(),
        FlexDirectionPlugin(),
        FlexWrapPlugin(),
        FlexGrowPlugin(),
        FlexShrinkPlugin(),
        FlexBasisPlugin(),
        JustifyContentPlugin(),
        AlignItemsPlugin(),
        AlignContentPlugin(),
        AlignSelfPlugin(),
        GridColumnsPlugin(),
        GridRowsPlugin(),
        OverflowPlugin(),
        OrderPlugin(),
        AspectRatioPlugin(),
        ColumnsPlugin(),
        ObjectFitPlugin(),
        ContainerPlugin(),
        ContainerTypePlugin(),
    ]
