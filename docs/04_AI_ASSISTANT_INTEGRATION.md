# AI Assistant Integration Guide

## Overview

This guide explains how to effectively use AI assistants (Claude, Cursor, etc.) with this project.

## Context Files

The project maintains two critical files for AI context:

1.  `.claude-context.md`: Tracks project state, architecture, and recent changes.
2.  `.bugs_tracker.md`: Tracks active bugs and known issues.

**Rule:** Always update these files after a significant coding session.

## System Prompts

When starting a new chat with an AI assistant, instruct it to:

1.  Read `docs/00_START_HERE.md` to understand the framework.
2.  Read `.claude-context.md` to understand the current state.
3.  Read `.bugs_tracker.md` to be aware of existing issues.

## Workflow

1.  **Start:** "Read the context files."
2.  **Work:** Ask for changes/features.
3.  **End:** "Update the context files with what we did."
