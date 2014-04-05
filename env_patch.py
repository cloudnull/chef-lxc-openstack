#!/usr/bin/env python

# Copyright 2014, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author Kevin.Carter@Rackspace.com

import json
import sys

def main(user, ip):
    """With an existing rpcs.json write a sevice URI into the file for vnc.

    :param user: ``str``
    :param ip: ``str``
    """
    # Open built JSON file
    with open('/home/%s/rpcs.json' % user, 'rb') as f:
        json_data = json.loads(f.read())

    # Create the new override syntax
    overrides = json_data['override_attributes']
    nova = overrides['nova']
    services = nova['services'] = {}
    # Add xvpvnc
    xvpvnc = services['xvpvnc-proxy'] = {}
    xvpvnc['uri'] = 'http://%s:6081/console' % ip
    # Add novnc
    novnc = services['novnc-proxy'] = {}
    novnc['uri'] = 'http://%s:6080/vnc_auto.html' % ip

    # Write the modified JSON file
    with open('/home/%s/rpcs.json' % user, 'wb') as f:
        f.write(json.dumps(json_data, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Not enough args, usage: %s user ip' % sys.argv[0])
    else:
        main(sys.argv[1], sys.argv[2])
