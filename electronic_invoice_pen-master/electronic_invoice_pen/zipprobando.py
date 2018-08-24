# -*- coding: utf-8 -*-

import base64
import os
import zipfile

from jinja2 import FileSystemLoader, Environment
from lxml import etree
from xml.etree.ElementTree import  ElementTree
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as etree


path_dir = os.path.dirname(os.path.realpath(__file__))
attach_dir = os.path.join(path_dir, 'attach')
loader = FileSystemLoader('./templates')
env = Environment(loader=loader)

root = Element('person')
tree = ElementTree(root)
name = Element('name')
root.append(name)
name.text='asdfasdfasdf'
root.set('id', '123')

print etree.tostring(root)
tree.write(open(r'c:\person.xml', 'w'))
tree.write(open(r'c:\personaa.xml', 'w'))

zf = zipfile.ZipFile(r'c:\probando.zip', mode='w')
zf.writestr(zipfile.ZipInfo('empty/'), '')
zf.write(r'c:\personaa.xml', 'w')
for root, dirs, files in os.walk('files'):
    for f in files:
        zf.write(os.path.join(root, f))
os.remove(r'c:\personaa.xml')
zf.write(r'c:\person.xml')
zf.close()

print zf.namelist()
