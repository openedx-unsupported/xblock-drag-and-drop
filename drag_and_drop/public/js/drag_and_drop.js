function DragAndDropBlock(runtime, element) {
    function publish_event(data) {
      $.ajax({
          type: "POST",
          url: runtime.handlerUrl(element, 'publish_event'),
          data: JSON.stringify(data)
      });
    }

    var move_item_to_bucket = function(item_id, bucket_id) {
        // select the items with the matching item_id. Note there can be
        // more than one since we are using 'clone' draggables
        items = $('.draggable-item[data-id="' + item_id + '"]', element);
        item = items.first();
        var item_list = item.parent('.draggable-item-list');

        // user put the item in the right bucket
        bucket = $('.draggable-target[data-id="' + bucket_id + '"]', element);
        bucket_landing = bucket.find('.draggable-target-landing');

        // copy over the dragged item into a new DOM element
        var copy = item.clone();

        // If the dragged item has no-bg-color associated with it, be sure
        // to make sure that the dropped item also has that characteristic
        if (copy.hasClass('draggable-item-no-bg-color')) {
            copy.attr('class', 'dropped-correct-item dropped-correct-item-no-bg-color');
        } else {
            copy.attr('class', 'dropped-correct-item');
        }
        copy.removeAttr('style');

        // delete the original one(s)
        items.remove();

        var dropped_list = bucket.find('.dropped-items');

        dropped_list.append(copy);

        // now make sure the row has all the same size as the size of the
        // drop landing area can grow as we add new elements
        var new_height = bucket_landing.outerHeight();
        var bucket_row = bucket.data('row');
        $('.draggable-target',element).each(function(index, el) {
            var ele = $(el);
            if (ele.data('row') === bucket_row && ele.data('id') !== item_id) {
                var ele_landing = ele.find('.draggable-target-landing');
                ele_landing.css('min-height', new_height);
            }
        });
    };

    // set up the draggable items
    $('.draggable-item', element).draggable({
        revert: function(evt, ui) {
            if (!evt) {
                $('.draggable-item').removeClass("draggable-item-original");
                return true;
            } else {
                return false;
            }
        },
        start: function(evt, ui) {
            $(ui.helper.context).addClass("draggable-item-original");
            // on drag start hide any feedback that might be open
            $('.drag-and-drop-feedback', element).css('display', 'none');

            var item_id = $(evt.target).data("id");
            publish_event({event_type:'drag-and-drop.item.picked-up', item_id:item_id});
        },
        drop: function(evt, ui) {
            $(ui.helper.context).removeClass("draggable-item-original");
            $(ui.helper).remove();
        },
        helper: "clone"
    });

    // set up the droppable items
    $('.draggable-target-landing', element).droppable({
        drop: function(event, el) {

            $('.draggable-item').removeClass("draggable-item-original");

            // Handle the drop events
            var draggable = el.draggable;
            var item_id = draggable.data('id');
            var correct_bucket = draggable.data('correctbucket');
            var target = $(event.target);
            var bucket = target.parent('.draggable-target');
            var bucket_id = bucket.data('id');

            /* see if the user put the draggable in the right bucket */
            var right_bucket = draggable.data('correctbucket');

            // make a callback to the server
            var handlerUrl = runtime.handlerUrl(element, 'student_on_item_drop');

            data = {
                drop_event: {
                    item_id: item_id,
                    bucket_id: bucket_id
                }
            };

            // call back to the server to report that the user dropped the item
            $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
                if (response.result === 'success') {

                    draggable.data('id', '');
                    move_item_to_bucket(item_id, bucket_id);
                }

                // show feedback
                if (response.msg !== undefined && response.msg !== null) {
                    $('.drag-and-drop-feedback-content', element).html(response.msg);
                    $('.drag-and-drop-feedback', element).css('display', 'block');
                }

                // show completed feedback, if present
                if (response.completed_feedback !== undefined && response.completed_feedback !== null) {
                    $('.drag-and-drop-completed-feedback-content', element).html(response.completed_feedback);
                    $('.drag-and-drop-completed-feedback', element).removeClass('drag-and-drop-completed-feedback').addClass('drag-and-drop-completed-feedback-visible');
                }
            });

            // unfortunately, in order to get the "snap back on wrong answer feature working"
            // we need to use the 'correct-bucket' that is put on a data- attribute
            // We can't do this after the server callback finishes, because the jQueryUI
            // thinks the drop was accepted
            if (correct_bucket !== bucket_id) {
                draggable.draggable('option', 'revert', true);
                return false;
            }

        },
        hoverClass: "draggable-target-landing-hover"
    });

    //
    // now make sure that all the tops of the drop targets are the same size
    // in the same row so that things float the right way
    //
    var needed_height_per_row = {};
    var needed_height_drop_zone_per_row = {};

    // Calculate the max height of all the elements in a row (title/description)
    $('.draggable-target', element).each(function(index, el) {
        var ele = $(el);
        var top_height = ele.find('.draggable-target-top').height();
        var row = ele.data('row');

        if (row in needed_height_per_row) {
            if (top_height > needed_height_per_row[row])
                needed_height_per_row[row] = top_height;
        } else {
            needed_height_per_row[row] = top_height;
        }
    });

    // then apply the same height around all same top elements in the row
    $('.draggable-target', element).each(function(index, el) {
        var ele = $(el);
        var row = ele.data('row');
        var height = needed_height_per_row[row];
        ele.find('.draggable-target-top').height(height);
    });

    //
    // handler for the close button
    //
    $('.drag-and-drop-feedback-close', element).click(function(eventObj) {
        eventObj.preventDefault();
        eventObj.stopPropagation();
        $('.drag-and-drop-feedback', element).css('display', 'none');
        publish_event({event_type:'drag-and-drop.feedback.closed-manually'});
    });

    //
    // on page load get the state of the items and put them in the buckets if they have been
    // properly set
    //
    $.ajax(runtime.handlerUrl(element, 'get_item_state')).done(function(data){
        for (var item_id in data) {
            move_item_to_bucket(item_id, data[item_id]);
        }
    });

}
