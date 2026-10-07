[app]

title = Инженерный калькулятор
package.name = encalc
package.domain = uz.faxriddinov

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin,build,.git,__pycache__

version = 1.3
requirements = python3==3.12.10,hostpython3==3.12.10,kivy==2.3.1,requests==2.28.1,charset-normalizer==2.1.1,urllib3==1.26.20,idna==3.4,certifi

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a


[buildozer]

log_level = 2
warn_on_root = 1
