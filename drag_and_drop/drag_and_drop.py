# -*- coding: utf-8 -*-
#

# Imports ###########################################################

import logging
import textwrap
from lxml import etree
from xml.etree import ElementTree as ET

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from StringIO import StringIO

from .utils import render_template, AttrDict, load_resource


# Globals ###########################################################

log = logging.getLogger(__name__)


# Classes ###########################################################

class DragAndDropBlock(XBlock):
    """
    XBlock providing a video player for videos hosted on Brightcove
    """
    display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Drag and Drop"
    )

    data = String(help="XML contents to display for this module", scope=Scope.content, default=textwrap.dedent("""\
        <drag_and_drop schema_version='1'>
        </drag_and_drop>
        """))

    def student_view(self, context):
        """
        Player view, displayed to the student
        """

        xmltree = etree.fromstring(self.data)

        context = {
        }


        fragment = Fragment()
        fragment.add_content(render_template('/templates/html/drag_and_drop.html', context))
        fragment.add_css(load_resource('public/css/drag_and_drop.css'))
        fragment.add_javascript(load_resource('public/js/drag_and_drop.js'))

        fragment.initialize_js('DragAndDropBlock')

        return fragment

    def studio_view(self, context):
        """
        Editing view in Studio
        """
        fragment = Fragment()
        fragment.add_content(render_template('/templates/html/drag_and_drop_edit.html', {
            'self': self,
        }))
        fragment.add_javascript(load_resource('public/js/drag_and_drop_edit.js'))

        fragment.initialize_js('DragAndDropEditBlock')

        return fragment

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):

        self.display_name = submissions['display_name']
        xml_content = submissions['data']

        try:
            etree.parse(StringIO(xml_content))
            self.data = xml_content
        except etree.XMLSyntaxError as e:
            return {
                'result': 'error',
                'message': e.message
            }

        return {
            'result': 'success',
        }
