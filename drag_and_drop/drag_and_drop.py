# -*- coding: utf-8 -*-
#

# Imports ###########################################################

import logging
import textwrap
import json
import webob
from lxml import etree
from xml.etree import ElementTree as ET

from xblock.core import XBlock
from xblock.fields import Scope, String, Dict, Float
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

    weight = Float(
        display_name="Weight",
        help="This is the maximum score that the user receives when he/she successfully completes the problem",
        scope=Scope.settings,
        default=1
    )

    item_state = Dict(
        help="JSON payload regarding how the student has interacted with the problem",
        scope=Scope.user_state
    )

    data = String(
        display_name="Drag and Drop",
        help="XML contents to display for this module",
        scope=Scope.content,
        default=textwrap.dedent("""
            <drag_and_drop schema_version='1'>
                <description>
                    <p>This is an example Drag and Drop problem</p>
                </description>
                <correct_feedback>
                    <p><strong>Terrific!</strong></p><p>You got everything correct!</p>
                </correct_feedback>
                <targets>
                    <bucket id='task1' title='Task 1'>
                        <description>
                            <span>This is target 1.</span>
                        </description>
                    </bucket>
                    <bucket id='task2' title='Task 2'>
                        <description>
                            <span>This is target 2.  Choose me!</span>
                        </description>
                    </bucket>
                    <bucket id='task3' title='Task 3'>
                        <description>
                            <span>This is target 3. Here I am!</span>
                        </description>
                    </bucket>
                    <bucket id='task4' title='Task 4'>
                        <description>
                            <span>This is target 4. Look here!</span>
                        </description>
                    </bucket>
                </targets>
                <items>
                    <item id='item1' correct_target='task1'>
                        <body>
                            <p>Item 1</p>
                        </body>
                        <correct_feedback>
                            <p>This was correct! Good job!</p>
                        </correct_feedback>
                        <incorrect_feedback>
                            <p>Sorry, try again!</p>
                        </incorrect_feedback>
                    </item>
                    <item id='item2' correct_target='task2'>
                        <body>
                            <p>Item 2</p>
                        </body>
                        <correct_feedback>
                            <p>Yep, you got it</p>
                        </correct_feedback>
                        <incorrect_feedback>
                            <p>Sorry, no dice!</p>
                        </incorrect_feedback>
                    </item>
                    <item id='item3'>
                        <body>
                            <p>Decoy</p>
                        </body>
                        <incorrect_feedback>
                            <p>This is just a decoy, silly person!</p>
                        </incorrect_feedback>
                    </item>
                    <item id='item4' correct_target='task3'>
                        <body>
                            <img src="//www.utexas.edu/law/sao/img/sunflower_small.png" />
                        </body>
                        <correct_feedback>
                            <p>Yes, sunflowers do like it here.</p>
                        </correct_feedback>
                        <incorrect_feedback>
                            <p>That is not where the sunflower belongs</p>
                        </incorrect_feedback>
                    </item>
                    <item id='item5' correct_target='task4' no_bg_color='true'>
                        <body>
                            <img src="//3.bp.blogspot.com/-zVV6yHfER04/UgPkN44z-yI/AAAAAAAABto/NAsyEHx3mFU/s1600/0209-NL-1992161-20130808.jpg" />
                        </body>
                        <correct_feedback>
                            <p>Correct, tulips do like to grow in Holland near a windmill</p>
                        </correct_feedback>
                        <incorrect_feedback>
                            <p>Not quite the right answer. Try again!</p>
                        </incorrect_feedback>
                    </item>
                </items>

            </drag_and_drop>
        """
        ))

    has_score = True

    def student_view(self, context):
        """
        Player view, displayed to the student
        """

        xmltree = etree.fromstring(self.data)

        # parse out all of the XML into nice friendly objects
        description = self._get_description(xmltree)
        items = self._get_items(xmltree)
        targets = self._get_targets(xmltree)

        draggable_target_class = 'draggable-target' if len(targets) > 1 else 'draggable-target-full-width'

        max_score_string = '({0} Point{1} Possible)'.format(int(self.weight),
            's' if self.weight > 1 else '') if self.weight else ''

        context = {
            'title': self.display_name,
            'description': description,
            'items': items,
            'targets': targets,
            'draggable_target_class': draggable_target_class,
            'max_score_string': max_score_string,
            'correct_feedback_class': 'drag-and-drop-completed-feedback',
        }

        max_items_to_be_correct = 0
        for item in items:
            # let's count the number of items that have a correct target (aka not a decoy)
            if item.correct_target:
                max_items_to_be_correct += 1

        # if student has completed this exercise then show the correct feedback
        if len(self.item_state) == max_items_to_be_correct:
            context['correct_feedback'] = self._get_correct_feedback(xmltree)
            context['correct_feedback_class'] = 'drag-and-drop-completed-feedback-visible'

        fragment = Fragment()
        fragment.add_content(render_template('/templates/html/drag_and_drop.html', context))
        fragment.add_css(load_resource('public/css/drag_and_drop.css'))
        fragment.add_javascript(load_resource('public/js/vendor/jquery-ui-1.10.4.custom.js'))
        fragment.add_javascript(load_resource('public/js/drag_and_drop.js'))

        fragment.initialize_js('DragAndDropBlock')

        return fragment

    @XBlock.json_handler
    def publish_event(self, data, suffix=''):

        try:
            event_type = data.pop('event_type')
        except KeyError as e:
            return {'result': 'error', 'message': 'Missing event_type in JSON data'}

        data['user_id'] = self.runtime.user_id

        self.runtime.publish(self, event_type, data)
        return {'result':'success'}

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
        max_score = submissions['max_score']

        if not max_score:
            # empty = default
            max_score = 1
        else:
            try:
                # not an integer, then default
                max_score = int(max_score)
            except:
                max_score = 1

        self.weight = max_score

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

    @XBlock.handler
    def get_item_state(self, request, suffix=''):
        return webob.response.Response(body=json.dumps(self.item_state))

    @XBlock.handler
    def clear_state(self, request, suffix=''):
        self.item_state = {}
        return webob.response.Response()

    @XBlock.json_handler
    def student_on_item_drop(self, submissions, suffix=''):
        drop_event = submissions['drop_event']
        item_id = drop_event['item_id']
        bucket_id = drop_event['bucket_id']

        xmltree = etree.fromstring(self.data)
        items = self._get_items(xmltree)
        correct_feedback = self._get_correct_feedback(xmltree)

        is_correct = False
        is_completed = False
        msg = None

        max_items_to_be_correct = 0
        for item in items:
            # let's count the number of items that have a correct target (aka not a decoy)
            if item.correct_target:
                max_items_to_be_correct += 1

            if item.id == item_id:
                # did the user place it in the right bucket?
                if item.correct_target == bucket_id:
                    # store the state that the user placed the item in the right bucket
                    # note we don't store incorrect placements, becuase the UI will snap
                    # it back to the item list dock
                    self.item_state[item_id] = bucket_id
                    is_correct = True

                    msg = item.correct_feedback
                else:
                    msg = item.incorrect_feedback

        # let's calculate if the user has placed all items in the correct bucket
        # but only if the current action was correct (e.g. don't give completed feedback)
        # if use contrinues to drop decoys
        completed_feedback = None
        if is_correct and len(self.item_state) == max_items_to_be_correct:
            is_completed = True
            if correct_feedback:
                completed_feedback = correct_feedback

            # publish a grading event when student completes this exercise
            # NOTE, we don't support partial credit
            try:
                self.runtime.publish(self, 'grade', {
                    'value': self.weight,
                    'max_value': self.weight,
                })
            except NotImplementedError:
                # Note, this publish method is unimplemented in Studio runtimes, so
                # we have to figure that we're running in Studio for now
                pass

        self.runtime.publish(self, 'drag-and-drop.item.dropped', {
            'user_id': self.runtime.user_id,
            'item_id': item_id,
            'location': bucket_id,
            'is_correct': is_correct,
        })

        if is_correct:
            return {
                'result': 'success',
                'msg': msg,
                'is_completed': is_completed,
                'completed_feedback': completed_feedback,
            }
        else:
            return {
                'result': 'failure',
                'msg': msg,
            }


    ######### HELPER METHODS ############
    def _inner_content(self, tag):
        """
        Helper method
        """
        inner_content = None
        if tag is not None:
            inner_content = u''.join(ET.tostring(e) for e in tag)

        return inner_content

    def _get_description(self, xmltree):
        """
        Parse the XML to get the description information
        """
        description = xmltree.find('description')
        if description is not None:
            return self._inner_content(description)
        return None

    def _get_correct_feedback(self, xmltree):
        """
        Parse the XML to get the feedback presented when the student
        answers everything correctly
        """
        return self._inner_content(xmltree.find('correct_feedback'))

    def _get_targets(self, xmltree):
        """
        Parse the XML to get the target information
        """

        targets_element= xmltree.find('targets')
        bucket_elements = targets_element.findall('bucket')
        buckets = []
        row = 1
        index = 0
        for bucket_element in bucket_elements:
            target_id = bucket_element.get('id')
            title = bucket_element.get('title')

            description = self._inner_content(bucket_element.find('description'))

            bucket = AttrDict()
            bucket.id = target_id
            bucket.title = title
            bucket.description = description
            bucket.row = row

            buckets.append(bucket)
            index += 1
            if not index % 2:
                row += 1

        return buckets

    def _get_items(self, xmltree):
        """
        Parse the XML to get the items information
        """

        items_element= xmltree.find('items')
        item_elements = items_element.findall('item')
        items = []
        for item_element in item_elements:
            item_id = item_element.get('id')
            correct_target = item_element.get('correct_target')  # note, this can be None
            no_bg_color = item_element.get('no_bg_color', False)

            body = self._inner_content(item_element.find('body'))

            # note, for items that do not have a target, this is an optional element
            correct_feedback_element = item_element.find('correct_feedback')
            correct_feedback = None
            if correct_feedback_element:
                correct_feedback = self._inner_content(correct_feedback_element)

            # but all items will expose an incorrect feedback
            incorrect_feedback = self._inner_content(item_element.find('incorrect_feedback'))

            item = AttrDict()
            item.id = item_id
            item.correct_target = correct_target
            item.body = body
            item.correct_feedback = correct_feedback
            item.incorrect_feedback = incorrect_feedback
            item.no_bg_color = no_bg_color

            items.append(item)

        return items

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [("Drag-and-drop scenario", "<vertical_demo><drag-and-drop/></vertical_demo>")]
