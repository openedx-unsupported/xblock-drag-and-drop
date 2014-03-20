function DragAndDropBlock(runtime, element) {
    // set up the draggable items
    $('.draggable-item', element).draggable({
        revert: function(evt) {
            return !evt;
        },
        start: function(evt) {
            // on drag start hide any feedback that might be open
            $('.drag-and-drop-feedback', element).css('display', 'none');
        }
    });

    // set up the droppable items
    $('.draggable-target-landing', element).droppable({
        drop: function(event, el) {
            // Handle the drop events
            var draggable = el.draggable;
            var item_id = draggable.data('id');
            var target = $(event.target);
            var bucket = target.parent('.draggable-target');
            var bucket_id = bucket.data('id');

            /* see if the user put the draggable in the right bucket */
            var right_bucket = draggable.data('correctbucket');

            // make a callback to the server
            var handlerUrl = runtime.handlerUrl(element, 'student_on_item_drop');
            data = {
                item_state: {
                    item_id: item_id,
                    bucket_id: bucket_id
                }
            };
            $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
                if (response.result === 'success') {
                    // user put the item in the right bucket
                    var draggable_list = draggable.parent('.draggable-item-list');

                    // copy over the dragged item into a new DOM element
                    var copy = draggable.clone();
                    copy.attr('class', 'dropped-correct-item');
                    copy.removeAttr('style');

                    // delete the original one
                    draggable.remove();

                    var dropped_list = target.find('.dropped-items');

                    dropped_list.append(copy);

                    // now make sure the row has all the same size as the size of the
                    // drop landing area can grow as we add new elements
                    var new_height = target.height();
                    var bucket_row = bucket.data('row');
                    $('.draggable-target',element).each(function(index, el) {
                        var ele = $(el);
                        if (ele.data('row') === bucket_row) {
                            var ele_landing = ele.find('.draggable-target-landing');
                            ele_landing.height(new_height);
                        }
                    });
                } else {
                    draggable.draggable('option', 'revert', true);
                    // alert(response.msg);
                }

                // show feedback
                if (response.msg !== undefined && response.msg !== null) {
                    $('.drag-and-drop-feedback-content', element).html(response.msg);
                    $('.drag-and-drop-feedback', element).css('display', 'block');
                }
            });
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
        var title_height = ele.find('.draggable-target-title').height();
        var desc_height = ele.find('.draggable-target-description').height();
        var row = ele.data('row');

        var top_height = (title_height > desc_height) ? title_height : desc_height;

        if (row in needed_height_per_row) {
            if (top_height > needed_height_per_row[row])
                needed_height_per_row[row] = top_height;
        } else {
            needed_height_per_row[row] = top_height;
        }
    });

    // then apply the same height around all same elements in the row
    $('.draggable-target', element).each(function(index, el) {
        var ele = $(el);
        var row = ele.data('row');
        var height = needed_height_per_row[row];
        ele.find('.draggable-target-title').height(height);
        ele.find('.draggable-target-description').height(height);
    });

    //
    // handler for the close button
    //
    $('.drag-and-drop-feedback-close', element).click(function(eventObj) {
        eventObj.preventDefault();
        eventObj.stopPropagation();
        $('.drag-and-drop-feedback', element).css('display', 'none');
    });
}
