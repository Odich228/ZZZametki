[app]
title = Notes App
package.name = notesapp
package.domain = org.notesapp

source.dir = .
source.include_exts = py,kv,png,jpg,atlas

version = 0.1

requirements = python3,kivy==2.3.0,requests

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = INTERNET
android.api = 33
android.minapi = 21
