[app]
title = MasterNet
package.name = masternet
package.domain = store.masternet
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,aiohttp,multidict,yarl,frozenlist,aiosignal,attrs
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.gradle_dependencies = 
android.permissions = INTERNET
android.accept_sdk_license = true

[buildozer]
log_level = 2
warn_on_root = 1

[requirements]
# All requirements are defined in the [app] section above
