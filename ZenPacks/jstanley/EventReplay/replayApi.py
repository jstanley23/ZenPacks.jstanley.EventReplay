'''
API interfaces and default implementations.
'''
import json
import logging

from zope.interface import implements

from Products import Zuul
from Products.ZenUI3.browser.streaming import StreamingView
from Products.ZenUtils.Ext import DirectRouter, DirectResponse
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade


