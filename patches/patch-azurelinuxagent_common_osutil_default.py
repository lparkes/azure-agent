$NetBSD$

Add NetBSD support

--- azurelinuxagent/common/osutil/default.py.orig	2023-07-27 00:44:46.000000000 +0000
+++ azurelinuxagent/common/osutil/default.py	2023-11-23 16:15:02.777416797 +0000
@@ -131,7 +131,7 @@
 
 class DefaultOSUtil(object):
     def __init__(self):
-        self.agent_conf_file_path = '/etc/waagent.conf'
+        self.agent_conf_file_path = '@PKG_SYSCONFDIR@/waagent.conf'
         self.selinux = None
         self.disable_route_warning = False
         self.jit_enabled = False
