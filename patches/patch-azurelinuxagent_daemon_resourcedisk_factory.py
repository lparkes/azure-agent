$NetBSD$

Add NetBSD support

--- azurelinuxagent/daemon/resourcedisk/factory.py.orig	2023-11-23 15:15:03.406128399 +0000
+++ azurelinuxagent/daemon/resourcedisk/factory.py	2023-11-23 15:15:32.708073699 +0000
@@ -18,6 +18,7 @@
 from azurelinuxagent.common.version import DISTRO_NAME, DISTRO_VERSION, DISTRO_FULL_NAME 
 from .default import ResourceDiskHandler
 from .freebsd import FreeBSDResourceDiskHandler
+from .netbsd import NetBSDResourceDiskHandler
 from .openbsd import OpenBSDResourceDiskHandler
 from .openwrt import OpenWRTResourceDiskHandler
 
@@ -31,6 +32,9 @@
     if distro_name == "openbsd":
         return OpenBSDResourceDiskHandler()
 
+    if distro_name == "netbsd":
+        return NetBSDResourceDiskHandler()
+
     if distro_name == "openwrt":
         return OpenWRTResourceDiskHandler()
 
