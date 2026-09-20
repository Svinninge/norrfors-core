# File version: v0.02
# Description: Package root for norrfors-core, shared building blocks across projects
# Author: Per Norrfors
# Created: 2026-09-20
# Modified: 2026-09-20 - Version 0.2.0, ships py.typed (Claude)
"""Shared building blocks reused across Per Norrfors' projects.

A module belongs here only once two projects already use it and it has had to be
changed in both places at least once. Business logic, UI and data models stay in
the projects: they look alike but drift apart, and a shared copy of them would
turn into a ball of flags.
"""

__version__ = "0.2.0"
