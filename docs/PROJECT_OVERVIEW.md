# Project Overview

GestureOS is a local Windows 11 touchless-control layer. It complements, rather than replaces, standard input for short sessions of pointing, scrolling, media control, and presentations.

## Product principles

- Safe by default: control must be deliberately armed; risky actions are blocked or require a long hold.
- Predictable over clever: reliable poses and clear feedback take priority over feature count.
- Local and private: video stays in memory on the PC and is not uploaded or saved by default.
- Accessible but honest: settings support different users; no unsupported accessibility claims are made.

## Release intent

v1.0 is a functional foundation: camera health, landmark overlay, safe mouse and media control, calibration, settings, dashboard, and debug status. v1.5 adds productivity features such as profiles and presentation controls. v2.0 considers custom gesture training and Gesture Studio. Spatial interaction, voice, and 3D features are experimental or deferred.

## Boundaries

GestureOS does not control elevated applications, UAC prompts, or the Windows lock screen. It does not execute arbitrary commands, upload camera data, or start the camera without an explicit user action.
