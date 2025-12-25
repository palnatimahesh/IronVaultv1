[app]
title = Iron Vault
package.name = ironvault
package.domain = org.ironvault
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# --- ICON CONFIGURATION ---
# The name of your icon file (must be in the same folder as main.py)
icon.filename = icon.png

version = 1.0.0
requirements = python3,kivy==2.2.0,kivymd==1.1.1,pillow,openssl,requests,urllib3,chardet,idna
orientation = portrait
osx.python_version = 3
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
