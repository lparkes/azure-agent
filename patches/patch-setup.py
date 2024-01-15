$NetBSD$

Add NetBSD support

--- setup.py.orig	2023-07-27 00:44:46.000000000 +0000
+++ setup.py	2023-11-23 15:56:01.114417297 +0000
@@ -74,6 +74,12 @@
     data_files.append((dest, src))
 
 
+def set_netbsd_rc_files(data_files, dest="/etc/rc.d/", src=None):
+    if src is None:
+        src = ["init/netbsd/waagent"]
+    data_files.append((dest, src))
+
+
 def set_openbsd_rc_files(data_files, dest="/etc/rc.d/", src=None):
     if src is None:
         src = ["init/openbsd/waagent"]
@@ -207,6 +213,10 @@
         set_bin_files(data_files, dest=agent_bin_path)
         set_conf_files(data_files, src=["config/freebsd/waagent.conf"])
         set_freebsd_rc_files(data_files)
+    elif name == 'netbsd':
+        set_bin_files(data_files, dest=agent_bin_path)
+        set_conf_files(data_files, src=["config/netbsd/waagent.conf"])
+        set_netbsd_rc_files(data_files)
     elif name == 'openbsd':
         set_bin_files(data_files, dest=agent_bin_path)
         set_conf_files(data_files, src=["config/openbsd/waagent.conf"])
