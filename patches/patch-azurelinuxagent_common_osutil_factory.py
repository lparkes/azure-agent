$NetBSD$

Add NetBSD support

--- azurelinuxagent/common/osutil/factory.py.orig	2023-11-23 13:42:21.562319028 +0000
+++ azurelinuxagent/common/osutil/factory.py	2023-11-23 13:43:02.598536144 +0000
@@ -33,6 +33,7 @@
 from .iosxe import IosxeOSUtil
 from .mariner import MarinerOSUtil
 from .nsbsd import NSBSDOSUtil
+from .netbsd import NetBSDOSUtil
 from .openbsd import OpenBSDOSUtil
 from .openwrt import OpenWRTOSUtil
 from .redhat import RedhatOSUtil, Redhat6xOSUtil, RedhatOSModernUtil
@@ -133,6 +134,9 @@
     if distro_name == "freebsd":
         return FreeBSDOSUtil()
 
+    if distro_name == "netbsd":
+        return NetBSDOSUtil()
+
     if distro_name == "openbsd":
         return OpenBSDOSUtil()
 
