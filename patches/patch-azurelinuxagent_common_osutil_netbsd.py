$NetBSD$

--- azurelinuxagent/common/osutil/netbsd.py.orig	2024-01-27 21:38:57.582385297 +0000
+++ azurelinuxagent/common/osutil/netbsd.py
@@ -0,0 +1,294 @@
+# Microsoft Azure Linux Agent
+#
+# Copyright 2018 Microsoft Corporation
+# Copyright 2017 Reyk Floeter <reyk@openbsd.org>
+# Copyright 2023 Stephen Borrill <sborrill@netbsd.org>
+#
+# Licensed under the Apache License, Version 2.0 (the "License");
+# you may not use this file except in compliance with the License.
+# You may obtain a copy of the License at
+#
+#     http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing, software
+# distributed under the License is distributed on an "AS IS" BASIS,
+# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+# See the License for the specific language governing permissions and
+# limitations under the License.
+#
+# Requires Python 2.6+ and OpenSSL 1.0+
+
+import os
+import re
+import time
+import glob
+import datetime
+
+import azurelinuxagent.common.utils.fileutil as fileutil
+import azurelinuxagent.common.utils.shellutil as shellutil
+import azurelinuxagent.common.logger as logger
+import azurelinuxagent.common.conf as conf
+
+from azurelinuxagent.common.exception import OSUtilError
+from azurelinuxagent.common.osutil.default import DefaultOSUtil
+
+UUID_PATTERN = re.compile(
+    r'^\s*[A-F0-9]{8}(?:\-[A-F0-9]{4}){3}\-[A-F0-9]{12}\s*$',
+    re.IGNORECASE)
+
+
+class NetBSDOSUtil(DefaultOSUtil):
+
+    def __init__(self):
+        super(NetBSDOSUtil, self).__init__()
+        self.jit_enabled = True
+        self._scsi_disks_timeout_set = False
+
+    @staticmethod
+    def get_agent_bin_path():
+        return "/usr/pkg/sbin"
+
+    def get_instance_id(self):
+        # This value matches the Azure vmId field for the vm.
+        ret, output = shellutil.run_get_output("sysctl -n machdep.dmi.system-uuid")
+        if ret != 0 or UUID_PATTERN.match(output) is None:
+            return ""
+        return output.strip()
+
+    def set_hostname(self, hostname):
+        fileutil.write_file("/etc/myname", "{}\n".format(hostname))
+        self._run_command_without_raising(["hostname", hostname], log_error=False)
+
+    def restart_ssh_service(self):
+        return shellutil.run('/etc/rc.d sshd restart', chk_err=False)
+
+    def start_agent_service(self):
+        return shellutil.run('/etc/rc.d/{0} start'.format(self.service_name), chk_err=False)
+
+    def stop_agent_service(self):
+        return shellutil.run('/etc/rc.d/{0} stop'.format(self.service_name), chk_err=False)
+
+#    def register_agent_service(self):
+#        shellutil.run('chmod 0555 /etc/rc.d/{0}'.format(self.service_name), chk_err=False)
+#        return shellutil.run('rcctl enable {0}'.format(self.service_name), chk_err=False)
+#
+#    def unregister_agent_service(self):
+#        return shellutil.run('rcctl disable {0}'.format(self.service_name), chk_err=False)
+
+    def del_account(self, username):
+        if self.is_sys_user(username):
+            logger.error("{0} is a system user. Will not delete it.", username)
+        self._run_command_without_raising(["touch", "/var/run/utmp"])
+        self._run_command_without_raising(["userdel", "-r", username])
+        self.conf_sudoer(username, remove=True)
+
+    def chpasswd(self, username, password, crypt_id=6, salt_len=10):
+        if self.is_sys_user(username):
+            raise OSUtilError(("User {0} is a system user. "
+                               "Will not set passwd.").format(username))
+        output = self._run_command_raising_OSUtilError(['encrypt'], cmd_input=password,
+                                                       err_msg="Failed to encrypt password for {0}".format(username))
+        passwd_hash = output.strip()
+        self._run_command_raising_OSUtilError(['usermod', '-p', passwd_hash, username],
+                                              err_msg="Failed to set password for {0}".format(username))
+
+    def del_root_password(self):
+        ret, output = shellutil.run_get_output('usermod -p "*" root')
+        if ret:
+            raise OSUtilError("Failed to delete root password: "
+                              "{0}".format(output))
+
+    def get_if_mac(self, ifname):
+        data = self._get_net_info()
+        if data[0] == ifname:
+            return data[2].replace(':', '').upper()
+        return None
+
+    def get_first_if(self):
+        return self._get_net_info()[:2]
+
+    def route_add(self, net, mask, gateway):
+        cmd = 'route add {0} {1} {2}'.format(net, gateway, mask)
+        return shellutil.run(cmd, chk_err=False)
+
+    def is_missing_default_route(self):
+        ret = shellutil.run("route -n get default", chk_err=False)
+        if ret == 0:
+            return False
+        return True
+
+    def is_dhcp_enabled(self):
+        """
+        Returns True if the DHCP client service is running.
+        """
+        dhcpcd = shellutil.run_command(["sh", "-c", ". /etc/rc.conf ; echo $dhcpcd"])
+        return dhcpcd == "YES\n"
+
+    def start_dhcp_service(self):
+        """
+        Start the DHCP client service assuming it is enabled.
+        """
+        # dhcpcd holds stdout and stderr open and so our default
+        # behaviour of waiting for the pipes to be closed won't work.
+        shellutil.run_command(["/etc/rc.d/dhcpcd", "start"], stdout=None, stderr=None)
+
+    def stop_dhcp_service(self):
+        """
+        Stop the DHCP client service assuming it is enabled.
+        """
+        shellutil.run_command(["/etc/rc.d/dhcpcd", "stop"])
+
+    def get_dhcp_lease_endpoint(self):
+        """
+        Extract the Azure endpoint from the DHCP lease.
+        """
+        logger.info('Getting endpoint from dhcpcd -U')
+        cmd = 'dhcpcd -U {} | grep azureendpoint'.format(self.get_first_if()[0])
+        status, output = shellutil.run_get_output(cmd, chk_err=True)
+        if status == 0:
+            ipaddr = output.split("=")[-1].strip()
+            logger.info('Found endpoint IP address {} from dhcpcd'.format(ipaddr))
+            return ipaddr
+        else:
+            logger.warn('Azure endpoint was not found in the output from dhcpcd -U')
+            logger.warn('Make sure dhcpcd is being started with the -w flag')
+            logger.warn('Make sure dhcpcd understands the Azure endpoint option')
+            return None
+
+    def allow_dhcp_broadcast(self):
+        pass
+
+    def set_route_for_dhcp_broadcast(self, ifname):
+        return shellutil.run("route add 255.255.255.255 -iface "
+                             "{0}".format(ifname), chk_err=False)
+
+    def remove_route_for_dhcp_broadcast(self, ifname):
+        shellutil.run("route delete 255.255.255.255 -iface "
+                      "{0}".format(ifname), chk_err=False)
+
+    # get_dhcp_pid is used to monitor for DHCP client restarts
+    def get_dhcp_pid(self):
+        return self._get_dhcp_pid(["cat", "/var/run/dhcpcd/pid"])
+
+    def get_dvd_device(self, dev_dir='/dev'):
+        pattern = r'cd[0-9]c'
+        for dvd in [re.match(pattern, dev) for dev in os.listdir(dev_dir)]:
+            if dvd is not None:
+                return "/dev/{0}".format(dvd.group(0))
+        raise OSUtilError("Failed to get DVD device")
+
+    def mount_dvd(self,
+                  max_retry=6,
+                  chk_err=True,
+                  dvd_device=None,
+                  mount_point=None,
+                  sleep_time=5):
+        if dvd_device is None:
+            dvd_device = self.get_dvd_device()
+        if mount_point is None:
+            mount_point = conf.get_dvd_mount_point()
+        if not os.path.isdir(mount_point):
+            os.makedirs(mount_point)
+
+        for retry in range(0, max_retry):
+            retcode = self.mount(dvd_device,
+                                mount_point, 
+                                option=["-o", "ro", "-t", "udf"], 
+                                chk_err=False) 
+            if retcode == 0:
+                logger.info("Successfully mounted DVD")
+                return
+            if retry < max_retry - 1:
+                mountlist = shellutil.run_get_output("/sbin/mount")[1]
+                existing = self.get_mount_point(mountlist, dvd_device)
+                if existing is not None:
+                    logger.info("{0} is mounted at {1}", dvd_device, existing)
+                    return
+                logger.warn("Mount DVD failed: retry={0}, ret={1}", retry,
+                            retcode)
+                time.sleep(sleep_time)
+        if chk_err:
+            raise OSUtilError("Failed to mount DVD.")
+
+    def eject_dvd(self, chk_err=True):
+        dvd = self.get_dvd_device()
+        retcode = shellutil.run("cdio eject {0}".format(dvd))
+        if chk_err and retcode != 0:
+            raise OSUtilError("Failed to eject DVD: ret={0}".format(retcode))
+
+    def restart_if(self, ifname, retries=3, wait=5):
+        # Restart dhclient only to publish hostname
+        shellutil.run("/sbin/dhclient {0}".format(ifname), chk_err=False)
+
+    def get_total_mem(self):
+        ret, output = shellutil.run_get_output("sysctl -n hw.physmem")
+        if ret:
+            raise OSUtilError("Failed to get total memory: {0}".format(output))
+        try:
+            return int(output)/1024/1024
+        except ValueError:
+            raise OSUtilError("Failed to get total memory: {0}".format(output))
+
+    def get_processor_cores(self):
+        ret, output = shellutil.run_get_output("sysctl -n hw.ncpu")
+        if ret:
+            raise OSUtilError("Failed to get processor cores.")
+
+        try:
+            return int(output)
+        except ValueError:
+            raise OSUtilError("Failed to get total memory: {0}".format(output))
+
+    def set_scsi_disks_timeout(self, timeout):
+        pass
+
+    def check_pid_alive(self, pid):  # pylint: disable=R1710
+        if not pid:
+            return
+        return shellutil.run('ps -p {0}'.format(pid), chk_err=False) == 0
+
+    @staticmethod
+    def _get_net_info():
+        """
+        There is no SIOCGIFCONF
+        on NetBSD - just parse ifconfig.
+        Returns strings: iface, inet4_addr, and mac
+        or 'None,None,None' if unable to parse.
+        We will sleep and retry as the network must be up.
+        """
+        iface = ''
+        inet = ''
+        mac = ''
+
+        ret, output = shellutil.run_get_output(
+            'ifconfig | grep -E "^hvn.:" | sed "s/:.*//g"', chk_err=False)
+        if ret:
+            raise OSUtilError("Can't find ether interface:{0}".format(output))
+        ifaces = output.split()
+        if not ifaces:
+            raise OSUtilError("Can't find ether interface.")
+        iface = ifaces[0]
+
+        ret, output = shellutil.run_get_output(
+            'ifconfig ' + iface, chk_err=False)
+        if ret:
+            raise OSUtilError("Can't get info for interface:{0}".format(iface))
+
+        for line in output.split('\n'):
+            if line.find('inet ') != -1:
+                inet = line.split()[1]
+            elif line.find('address: ') != -1:
+                mac = line.split()[1]
+        logger.verbose("Interface info: ({0},{1},{2})", iface, inet, mac)
+
+        return iface, inet, mac
+
+    def device_for_ide_port(self, port_id):
+        """
+        Return device name attached to ide port 'n'.
+        """
+        return "wd{0}".format(port_id)
+
+    @staticmethod
+    def get_total_cpu_ticks_since_boot():
+        return 0
