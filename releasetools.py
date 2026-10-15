# Copyright (C) 2009 The Android Open Source Project
# Copyright (c) 2011, The Linux Foundation. All rights reserved.
# Copyright (C) 2017-2018 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import common
import re

CHECK_VBMETA_SCRIPT = r"""#!/system/bin/sh
# Copyright (C) 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0

# Check a complete AVB v1 header before any OTA partition writes.
header=$(od -An -v -tu1 -N256 "$1") || exit 1
set -- $header
[ "$#" -eq 256 ] || exit 1
[ "$1 $2 $3 $4" = "65 86 66 48" ] || exit 1
shift 4
[ "$1 $2 $3 $4" = "0 0 0 1" ] || exit 1
shift 116
# Flags are big endian; accept VERIFICATION_DISABLED with optional
# HASHTREE_DISABLED, and reject reserved bits.
[ "$1 $2 $3" = "0 0 0" ] || exit 1
[ "$4" -eq 2 ] || [ "$4" -eq 3 ]
"""

def CheckVBMeta(info):
  # Samsung's bootloader protects this LUN before recovery starts.
  common.ZipWriteStr(info.output_zip, "check-vbmeta.sh", CHECK_VBMETA_SCRIPT)
  info.script.AppendExtra(
      'assert(package_extract_file("check-vbmeta.sh", "/tmp/check-vbmeta.sh"));')
  info.script.AppendExtra(
      'assert(run_program("/system/bin/sh", "/tmp/check-vbmeta.sh", '
      '"/dev/block/bootdevice/by-name/vbmeta") == 0 || '
      'abort("VBMETA verification must be disabled: flash vbmeta.img '
      'in Download mode before installing this OTA."));')
  info.script.AppendExtra('delete("/tmp/check-vbmeta.sh");')

def FullOTA_InstallBegin(info):
  CheckVBMeta(info)

def IncrementalOTA_InstallBegin(info):
  CheckVBMeta(info)

def FullOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def IncrementalOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def AddImage(info, basename, dest):
  path = "IMAGES/" + basename
  input_zip = getattr(info, "input_zip", None) or info.target_zip
  if path not in input_zip.namelist():
    return

  data = input_zip.read(path)
  common.ZipWriteStr(info.output_zip, basename, data)
  # Compare only image bytes: the physical partition can be larger.
  staged = "/tmp/" + basename
  info.script.AppendExtra(
      'assert(package_extract_file("%s", "%s"));' % (basename, staged))
  check = ('run_program("/system/bin/toybox", "cmp", "-s", "-n", '
           '"%d", "%s", "%s") == 0' % (len(data), staged, dest))
  # An already-matching protected image does not need a write.
  info.script.AppendExtra(
      'assert(%s || package_extract_file("%s", "%s"));' %
      (check, basename, dest))
  info.script.AppendExtra('assert(%s);' % check)
  info.script.AppendExtra('delete("%s");' % staged)

def OTA_InstallEnd(info):
  info.script.Print("Patching firmware images...")
  AddImage(info, "dtbo.img", "/dev/block/bootdevice/by-name/dtbo")
  AddImage(info, "init_boot.img", "/dev/block/bootdevice/by-name/init_boot")
  AddImage(info, "vbmeta_system.img", "/dev/block/bootdevice/by-name/vbmeta_system")
  AddImage(info, "vendor_boot.img", "/dev/block/bootdevice/by-name/vendor_boot")
  return
