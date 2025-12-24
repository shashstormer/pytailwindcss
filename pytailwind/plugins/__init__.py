"""
Plugin system for Tailwind CSS utilities.

This package provides the base classes and registry for
extending pytailwindcss with new utilities.
"""

from .base import UtilityPlugin, GeneratorContext
from .registry import PluginRegistry

__all__ = [
    'UtilityPlugin',
    'GeneratorContext', 
    'PluginRegistry',
]
