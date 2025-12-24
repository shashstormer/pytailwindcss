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
    """
    Plugin for aspect-ratio utilities (aspect-*).
    
    Supports:
    - aspect-auto
    - aspect-square (1/1)
    - aspect-video (16/9)
    - aspect-<ratio> (e.g. aspect-3/2, aspect-4/3)
    - aspect-[<value>] (arbitrary values)
    - aspect-(<custom-property>) (CSS variables)
    """
    
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
        # 1. Try resolving using standard mechanism (static values, arbitrary values)
        value = self.resolve_value(token, context)
        
        # 2. Handle aspect-(--var) shorthand
        if value is None and token.value.startswith('(') and token.value.endswith(')'):
            var_name = token.value[1:-1]
            value = f"var({var_name})"
            
        # 3. Handle numeric ratios (e.g. 3/2, 4/3)
        if value is None:
            # Check for simple fraction pattern N/N
            import re
            if re.match(r'^\d+(\.\d+)?/\d+(\.\d+)?$', token.value):
                value = token.value
        
        if value is None:
            return None
            
        return self.create_rule(token, 'aspect-ratio', value)


class ColumnsPlugin(UtilityPlugin):
    """
    Plugin for columns utilities (columns-*).
    
    Supports:
    - columns-<number> (1-12)
    - columns-<t-shirt-size> (3xs to 7xl)
    - columns-auto
    - columns-[<value>]
    - columns-(<custom-property>)
    """
    
    name = "columns"
    prefixes = ["columns"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        '3xs': 'var(--container-3xs, 16rem)',
        '2xs': 'var(--container-2xs, 18rem)',
        'xs': 'var(--container-xs, 20rem)',
        'sm': 'var(--container-sm, 24rem)',
        'md': 'var(--container-md, 28rem)',
        'lg': 'var(--container-lg, 32rem)',
        'xl': 'var(--container-xl, 36rem)',
        '2xl': 'var(--container-2xl, 42rem)',
        '3xl': 'var(--container-3xl, 48rem)',
        '4xl': 'var(--container-4xl, 56rem)',
        '5xl': 'var(--container-5xl, 64rem)',
        '6xl': 'var(--container-6xl, 72rem)',
        '7xl': 'var(--container-7xl, 80rem)',
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
        # 1. Standard resolution
        value = self.resolve_value(token, context)
        
        # 2. Handle columns-(--var) shorthand
        if value is None and token.value.startswith('(') and token.value.endswith(')'):
            var_name = token.value[1:-1]
            value = f"var({var_name})"
            
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




class BreakAfterPlugin(UtilityPlugin):
    """Plugin for break-after utilities."""
    name = "break-after"
    prefixes = ["break-after"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'avoid': 'avoid',
        'all': 'all',
        'avoid-page': 'avoid-page',
        'page': 'page',
        'left': 'left',
        'right': 'right',
        'column': 'column',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == "break-after"
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'break-after', value)


class BreakBeforePlugin(UtilityPlugin):
    """Plugin for break-before utilities."""
    name = "break-before"
    prefixes = ["break-before"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'avoid': 'avoid',
        'all': 'all',
        'avoid-page': 'avoid-page',
        'page': 'page',
        'left': 'left',
        'right': 'right',
        'column': 'column',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == "break-before"
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'break-before', value)


class BreakInsidePlugin(UtilityPlugin):
    """Plugin for break-inside utilities."""
    name = "break-inside"
    prefixes = ["break-inside"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'avoid': 'avoid',
        'avoid-page': 'avoid-page',
        'avoid-column': 'avoid-column',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == "break-inside"
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'break-inside', value)


class BoxDecorationBreakPlugin(UtilityPlugin):
    """Plugin for box-decoration-break utilities (box-decoration-*)."""
    name = "box-decoration-break"
    prefixes = ["box-decoration"]
    
    STATIC_VALUES = {
        'clone': 'clone',
        'slice': 'slice',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == "box-decoration"
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'box-decoration-break', value)


class BoxSizingPlugin(UtilityPlugin):
    """Plugin for box-sizing utilities (box-*)."""
    name = "box-sizing"
    prefixes = ["box"]
    
    STATIC_VALUES = {
        'border': 'border-box',
        'content': 'content-box',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == "box"
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'box-sizing', value)



class FloatPlugin(UtilityPlugin):
    """Plugin for float utilities (float-*)."""
    name = "float"
    prefixes = ["float"]
    
    STATIC_VALUES = {
        'right': 'right',
        'left': 'left',
        'none': 'none',
        'start': 'inline-start',
        'end': 'inline-end',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'float'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'float', value)


class ClearPlugin(UtilityPlugin):
    """Plugin for clear utilities (clear-*)."""
    name = "clear"
    prefixes = ["clear"]
    
    STATIC_VALUES = {
        'left': 'left',
        'right': 'right',
        'both': 'both',
        'none': 'none',
        'start': 'inline-start',
        'end': 'inline-end',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'clear'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None:
            return None
        return self.create_rule(token, 'clear', value)


class IsolationPlugin(UtilityPlugin):
    """Plugin for isolation utilities (isolate, isolation-auto)."""
    name = "isolation"
    prefixes = ["isolate", "isolation"]
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility in ('isolate', 'isolation')
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.utility == 'isolate':
            return self.create_rule(token, 'isolation', 'isolate')
        if token.utility == 'isolation' and token.value == 'auto':
            return self.create_rule(token, 'isolation', 'auto')
        return None


class ObjectPositionPlugin(UtilityPlugin):
    """Plugin for object-position utilities (object-*)."""
    name = "object-position"
    prefixes = ["object"]
    
    STATIC_VALUES = {
        'bottom': 'bottom',
        'center': 'center',
        'left': 'left',
        'right': 'right',
        'top': 'top',
        'bottom-left': 'bottom left',
        'bottom-right': 'bottom right',
        'top-left': 'top left',
        'top-right': 'top right',
    }
    
    @property
    def static_values(self) -> Dict[str, str]:
        return self.STATIC_VALUES
    
    @property
    def supports_arbitrary(self) -> bool:
        return True
    
    def match(self, token: TailwindToken) -> bool:
        if token.utility != 'object':
            return False
        # Avoid conflict with ObjectFitPlugin (contain, cover, etc.)
        if token.value in ('contain', 'cover', 'fill', 'scale-down', 'none') and token.value_type == ValueType.STATIC:
            return False
        return True
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        value = self.resolve_value(token, context)
        if value is None and token.value.startswith('(') and token.value.endswith(')'):
             var_name = token.value[1:-1]
             value = f"var({var_name})"
        
        if value is None:
            return None
        return self.create_rule(token, 'object-position', value)


class OverscrollPlugin(UtilityPlugin):
    """Plugin for overscroll-behavior utilities."""
    name = "overscroll"
    prefixes = ["overscroll"]
    
    STATIC_VALUES = {
        'auto': 'auto',
        'contain': 'contain',
        'none': 'none',
    }
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility == 'overscroll'
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.value not in self.STATIC_VALUES:
            return None
        value = self.STATIC_VALUES[token.value]
        
        prop = 'overscroll-behavior'
        if token.modifier == 'x': prop += '-x'
        elif token.modifier == 'y': prop += '-y'
        
        return self.create_rule(token, prop, value)


class VisibilityPlugin(UtilityPlugin):
    """Plugin for visibility utilities."""
    name = "visibility"
    prefixes = ["visible", "invisible", "collapse"]
    
    def match(self, token: TailwindToken) -> bool:
        return token.utility in self.prefixes
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if token.utility == 'visible':
            return self.create_rule(token, 'visibility', 'visible')
        if token.utility == 'invisible':
            return self.create_rule(token, 'visibility', 'hidden')
        if token.utility == 'collapse':
            return self.create_rule(token, 'visibility', 'collapse')
        return None


class SrOnlyPlugin(UtilityPlugin):
    """Plugin for screen-reader utilities."""
    name = "sr-only"
    prefixes = ["sr", "not-sr"]
    
    def match(self, token: TailwindToken) -> bool:
        return token.raw == "sr-only" or token.raw == "not-sr-only" or \
               (token.utility == "sr" and token.value == "only") or \
               (token.utility == "not-sr" and token.value == "only")
        
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        if "not-sr" in token.raw or "not-sr" in token.utility:
             return self.create_multi_rule(token, {
               "position": "static", "width": "auto", "height": "auto",
               "padding": "0", "margin": "0", "overflow": "visible",
               "clip": "auto", "white-space": "normal"
           })
        return self.create_multi_rule(token, {
           "position": "absolute", "width": "1px", "height": "1px",
           "padding": "0", "margin": "-1px", "overflow": "hidden",
           "clip": "rect(0, 0, 0, 0)", "white-space": "nowrap",
           "border-width": "0"
       })


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
        BreakAfterPlugin(),
        BreakBeforePlugin(),
        BreakInsidePlugin(),
        BoxDecorationBreakPlugin(),
        BoxSizingPlugin(),
        FloatPlugin(),
        ClearPlugin(),
        IsolationPlugin(),
        ObjectPositionPlugin(),
        OverscrollPlugin(),
        VisibilityPlugin(),
        SrOnlyPlugin(),
    ]
