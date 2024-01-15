$NetBSD$

Add NetBSD support

--- azurelinuxagent/common/version.py.orig	2023-11-23 15:12:46.147809899 +0000
+++ azurelinuxagent/common/version.py	2023-11-23 15:13:27.075744099 +0000
@@ -107,6 +107,9 @@
     if 'FreeBSD' in platform.system():
         release = re.sub('\-.*\Z', '', ustr(platform.release()))  # pylint: disable=W1401
         osinfo = ['freebsd', release, '', 'freebsd']
+    elif 'NetBSD' in platform.system():
+        release = re.sub('\-.*\Z', '', ustr(platform.release()))  # pylint: disable=W1401
+        osinfo = ['netbsd', release, '', 'netbsd']
     elif 'OpenBSD' in platform.system():
         release = re.sub('\-.*\Z', '', ustr(platform.release()))  # pylint: disable=W1401
         osinfo = ['openbsd', release, '', 'openbsd']
