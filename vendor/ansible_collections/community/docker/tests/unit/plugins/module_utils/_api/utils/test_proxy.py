# -*- coding: utf-8 -*-
# This code is part of the Ansible collection community.docker, but is an independent component.
# This particular file, and this file only, is based on the Docker SDK for Python (https://github.com/docker/docker-py/)
#
# Copyright (c) 2016-2022 Docker, Inc.
#
# It is licensed under the Apache 2.0 license (see LICENSES/Apache-2.0.txt in this collection)
# SPDX-License-Identifier: Apache-2.0

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest
import sys

import pytest

if sys.version_info < (2, 7):
    pytestmark = pytest.mark.skip('Python 2.6 is not supported')

from ansible_collections.community.docker.plugins.module_utils._api.utils.proxy import ProxyConfig


HTTP = 'http://test:80'
HTTPS = 'https://test:443'
FTP = 'ftp://user:password@host:23'
NO_PROXY = 'localhost,.localdomain'
CONFIG = ProxyConfig(http=HTTP, https=HTTPS, ftp=FTP, no_proxy=NO_PROXY)
ENV = {
    'http_proxy': HTTP,
    'HTTP_PROXY': HTTP,
    'https_proxy': HTTPS,
    'HTTPS_PROXY': HTTPS,
    'ftp_proxy': FTP,
    'FTP_PROXY': FTP,
    'no_proxy': NO_PROXY,
    'NO_PROXY': NO_PROXY,
}


class ProxyConfigTest(unittest.TestCase):

    def test_from_dict(self):
        config = ProxyConfig.from_dict({
            'httpProxy': HTTP,
            'httpsProxy': HTTPS,
            'ftpProxy': FTP,
            'noProxy': NO_PROXY
        })
        self.assertEqual(CONFIG.http, config.http)
        self.assertEqual(CONFIG.https, config.https)
        self.assertEqual(CONFIG.ftp, config.ftp)
        self.assertEqual(CONFIG.no_proxy, config.no_proxy)

    def test_new(self):
        config = ProxyConfig()
        self.assertIsNone(config.http)
        self.assertIsNone(config.https)
        self.assertIsNone(config.ftp)
        self.assertIsNone(config.no_proxy)

        config = ProxyConfig(http='a', https='b', ftp='c', no_proxy='d')
        self.assertEqual(config.http, 'a')
        self.assertEqual(config.https, 'b')
        self.assertEqual(config.ftp, 'c')
        self.assertEqual(config.no_proxy, 'd')

    def test_truthiness(self):
        assert not ProxyConfig()
        assert ProxyConfig(http='non-zero')
        assert ProxyConfig(https='non-zero')
        assert ProxyConfig(ftp='non-zero')
        assert ProxyConfig(no_proxy='non-zero')

    def test_environment(self):
        self.assertDictEqual(CONFIG.get_environment(), ENV)
        empty = ProxyConfig()
        self.assertDictEqual(empty.get_environment(), {})

    def test_inject_proxy_environment(self):
        # Proxy config is non null, env is None.
        self.assertSetEqual(
            set(CONFIG.inject_proxy_environment(None)),
            set('{k}={v}'.format(k=k, v=v) for k, v in ENV.items()))

        # Proxy config is null, env is None.
        self.assertIsNone(ProxyConfig().inject_proxy_environment(None), None)

        env = ['FOO=BAR', 'BAR=BAZ']

        # Proxy config is non null, env is non null
        actual = CONFIG.inject_proxy_environment(env)
        expected = ['{k}={v}'.format(k=k, v=v) for k, v in ENV.items()] + env
        # It's important that the first 8 variables are the ones from the proxy
        # config, and the last 2 are the ones from the input environment
        self.assertSetEqual(set(actual[:8]), set(expected[:8]))
        self.assertSetEqual(set(actual[-2:]), set(expected[-2:]))

        # Proxy is null, and is non null
        self.assertListEqual(ProxyConfig().inject_proxy_environment(env), env)
