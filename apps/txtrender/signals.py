"""
Signals declaration for the text rendering app.
"""

from django.dispatch import Signal


# Emitted when the rendering engine is altered.
render_engine_changed = Signal(providing_args=[])
