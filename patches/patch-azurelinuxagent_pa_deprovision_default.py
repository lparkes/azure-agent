kx$NetBSD$

Add NetBSD support

--- azurelinuxagent/pa/deprovision/default.py.orig	2023-11-23 13:54:24.198358728 +0000
+++ azurelinuxagent/pa/deprovision/default.py	2023-11-23 13:55:02.034515274 +0000
@@ -104,7 +104,7 @@
         files = ['/root/.bash_history', conf.get_agent_log_file()]
         actions.append(DeprovisionAction(fileutil.rm_files, files))
 
-        # For OpenBSD
+        # For NetBSD and OpenBSD
         actions.append(DeprovisionAction(fileutil.rm_files,
                                          ["/etc/random.seed",
                                           "/var/db/host.random",
@@ -123,7 +123,7 @@
         dirs_to_del = ["/var/lib/dhclient", "/var/lib/dhcpcd", "/var/lib/dhcp"]
         actions.append(DeprovisionAction(fileutil.rm_dirs, dirs_to_del))
 
-        # For FreeBSD and OpenBSD
+        # For FreeBSD, NetBSD and OpenBSD
         actions.append(DeprovisionAction(fileutil.rm_files,
                                          ["/var/db/dhclient.leases.*"]))
 
