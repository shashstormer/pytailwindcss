"""
Plugin registry for managing and dispatching to utility plugins.
"""

from typing import List, Optional, Dict, Type, Callable
from .base import UtilityPlugin, GeneratorContext
from ..parser import TailwindToken
from ..ast import Rule


class PluginRegistry:
    """
    Registry for utility plugins.
    
    Manages registration, lookup, and dispatching of plugins
    based on utility prefixes.
    """
    
    def __init__(self):
        self._plugins: List[UtilityPlugin] = []
        self._prefix_index: Dict[str, List[UtilityPlugin]] = {}
        self._name_index: Dict[str, UtilityPlugin] = {}
    
    def register(self, plugin: UtilityPlugin) -> None:
        """
        Register a utility plugin.
        
        Args:
            plugin: Plugin instance to register
            
        Raises:
            ValueError: If plugin with same name already registered
        """
        if plugin.name in self._name_index:
            raise ValueError(f"Plugin '{plugin.name}' is already registered")
        
        self._plugins.append(plugin)
        self._name_index[plugin.name] = plugin
        
        for prefix in plugin.prefixes:
            if prefix not in self._prefix_index:
                self._prefix_index[prefix] = []
            self._prefix_index[prefix].append(plugin)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin by name.
        
        Args:
            name: Plugin name to unregister
            
        Returns:
            True if plugin was found and removed, False otherwise
        """
        if name not in self._name_index:
            return False
        
        plugin = self._name_index.pop(name)
        self._plugins.remove(plugin)
        
        for prefix in plugin.prefixes:
            if prefix in self._prefix_index:
                self._prefix_index[prefix].remove(plugin)
                if not self._prefix_index[prefix]:
                    del self._prefix_index[prefix]
        
        return True
    
    def get_plugin(self, name: str) -> Optional[UtilityPlugin]:
        """Get plugin by name."""
        return self._name_index.get(name)
    
    def find_plugin(self, token: TailwindToken) -> Optional[UtilityPlugin]:
        """
        Find plugin that handles the given token.
        
        Args:
            token: Parsed Tailwind class token
            
        Returns:
            Plugin that matches the token, or None
        """
        # Try exact utility match
        candidates = self._prefix_index.get(token.utility, [])
        
        for plugin in candidates:
            if plugin.match(token):
                return plugin
        
        # Try with full utility (including modifier)
        if token.modifier:
            full_utility = token.full_utility
            candidates = self._prefix_index.get(full_utility, [])
            for plugin in candidates:
                if plugin.match(token):
                    return plugin
        
        return None
    
    def generate(self, token: TailwindToken, context: GeneratorContext) -> Optional[Rule]:
        """
        Generate CSS for token using registered plugins.
        
        Args:
            token: Parsed Tailwind class token
            context: Generator context with theme values
            
        Returns:
            CSS Rule or None if no plugin handles the token
        """
        plugin = self.find_plugin(token)
        if plugin:
            return plugin.generate(token, context)
        return None
    
    def list_plugins(self) -> List[str]:
        """List all registered plugin names."""
        return list(self._name_index.keys())
    
    def list_prefixes(self) -> List[str]:
        """List all registered prefixes."""
        return list(self._prefix_index.keys())
    
    def __len__(self) -> int:
        return len(self._plugins)
    
    def __iter__(self):
        return iter(self._plugins)


def create_registry_with_defaults() -> PluginRegistry:
    """
    Create a registry pre-populated with default Tailwind plugins.
    
    Returns:
        PluginRegistry with all built-in utilities registered
    """
    from . import spacing, colors, layout, typography, effects
    
    registry = PluginRegistry()
    
    # Register spacing plugins
    for plugin in spacing.get_plugins():
        registry.register(plugin)
    
    # Register color plugins
    for plugin in colors.get_plugins():
        registry.register(plugin)
    
    # Register layout plugins
    for plugin in layout.get_plugins():
        registry.register(plugin)
    
    # Register typography plugins
    for plugin in typography.get_plugins():
        registry.register(plugin)
    
    # Register effects plugins
    for plugin in effects.get_plugins():
        registry.register(plugin)
    
    return registry
