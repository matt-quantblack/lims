$(function () {

    function render_dd_list(target, data) {
        $(target).empty();
        $(target).append($('<option>', {value: null, text: "---------"}));
        $.each(data, function (index, item) {
            $(target).append($('<option>', {value: item.id, text: item.name}));
            });
    }

    function render_list(target, data, render_string, should_clear_list) {

        if(should_clear_list)
            $(target).empty();


        $.each(data.data, function (index, item) {
            line_render = render_string;
            $.each(Object.keys(item), function (index, key) {
                  line_render = line_render.split("{"+key+"}").join(item[key]);
            });
          $(target).append($(line_render));

        });

        if(!data.more)
            $(".more-pages").hide()

        //toggle the table, loading and no items cards
        $('#table-card-load').hide();
        if(data.data.length == 0) {
            $('#table-card').hide();
            $('#table-card-none').show();
        }
        else {
            $('#table-card-none').hide();
            $('#table-card').show();
        }
    }


    function send_api_request(url, data, target, renderer, render_string, should_clear_list)
    {
        $.ajax({
        url: url,
        data: data,
        dataType: 'json',
        success: function (data) {
          if (data) {
              renderer(target, data, render_string, should_clear_list);
          }
        }
      });
    }


    //dynamic dropdown box selections based on a value from another field
    $("#id_client").change(function () {
       id = $(this).val();
       send_api_request("/api/linkednotifcationgroups",{ 'client_id': id}, '#id_notificationgroup', render_dd_list);
    });

    //page loads for lists
    if($("#item_list").length)
        apiurl = $("#apiurl").val();
        render_string = $("#renderstring").val();
        if($("#refid").length)
            refid = $("#refid").val();
        else
            refid = -1;
        send_api_request(apiurl,{ 'q': '', 'page': 1, 'refid':refid}, '#item_list tbody', render_list, render_string, true);



    //list searches
    $("#search-input").keyup(function () {
       text = $(this).val();
       apiurl = $("#apiurl").val();
       render_string = $("#renderstring").val();
       if($("#refid").length)
            refid = $("#refid").val();
        else
            refid = -1;
       send_api_request(apiurl,{ 'q': text, 'refid':refid}, '#item_list tbody', render_list, render_string, true);
    });


    //list more results
    $(".search-items-more").click(function () {
       text = $(this).val();
       page = $(this).attr('page');
       apiurl = $("#apiurl").val();
       render_string = $("#renderstring").val();
       if($("#refid").length)
            refid = $("#refid").val();
        else
            refid = -1;
       $(this).attr('page', parseInt(page)+1);
       send_api_request(apiurl,{ 'q': text, 'page': page, 'refid': refid}, '#item_list tbody', render_list, render_string, false);
    });

});
