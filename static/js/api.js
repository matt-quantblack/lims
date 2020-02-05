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
                liststr = "";
                if(Array.isArray(item[key])) {
                    $.each(item[key], function (index2) {
                        liststr += "<li>" + item[key][index2]["name"] + "</li>";
                    });

                    line_render = line_render.split("{"+key+"}").join(liststr);
                }
                else
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


    function send_api_request(url, data, onsuccess)
    {
        $.ajax({
        url: url,
        data: data,
        dataType: 'json',
        success: function (data) {
          onsuccess(data);
        }
      });
    }

    $("#confirm_selection").click(function() {
       apiurl = $("#confirmurl").val();
       backurl = $("#backurl").val();
       refid = $("#refid").val();

       ids = "";
        $("#selected_table tr").each(function() {
            ids += $(this).attr('id') + ",";
        });

       send_api_request(apiurl,{ 'ids': ids, 'refid':refid}, function() { window.location.replace(backurl) });
    });

    $("#add_items").click(function(){
            rows = $("#item_list tr.selected");
            rows.remove();
            $("#select_list").append(rows);
            $(".selected").removeClass("selected");
    });

    $(".selection_table").on('click', 'tr', function(){
            $(this).toggleClass("selected");
    });

    $("#jobsamples").on('click', '.jobsample', function(){
        if($(this).hasClass("selected"))
            $(this).removeClass("selected text-white bg-primary");
        else
            $(this).addClass("selected text-white bg-primary");
    });

    $("#assigntests").click(function () {
        job_id = $(this).attr('job_id');
        test_id = $("#testselect").attr('value');
        jobsample_id = -1;
        if($("#applyall:checked").length == 0)
        {
            jobsample_id = "";
            $(".jobsample.selected").each(function() {
                jobsample_id += $(this).attr('jobsampleid') + ",";
            });
        }

        $.ajax({
            url: '/api/assignsamples',
            data: {'job_id': job_id, 'jobsample_id': jobsample_id, 'test_id': test_id},
            success: function (data) {
                if (data) {
                    $("#jobsamples").html(data);
                }
            }
        });
       //$("#jobsamples").load('/api/assignsamples', {'job_id':1, 'jobsample_id':-1, 'test_id':3})
    });

    //dynamic dropdown box selections based on a value from another field
    $("#id_client").change(function () {
       id = $(this).val();

       send_api_request("/api/linkednotifcationgroups",{ 'client_id': id}, function(data) { render_dd_list('#id_notificationgroup', data);});
    });

    //page loads for lists
    if($("#item_list").length) {
        apiurl = $("#apiurl").val();
        render_string = $("#renderstring").val();
        if ($("#refid").length)
            refid = $("#refid").val();
        else
            refid = -1;
        send_api_request(apiurl, {
            'q': '',
            'page': 1,
            'refid': refid
        }, function(data) {render_list('#item_list tbody', data, render_string, true);});

    }


    //list searches
    $("#search-input").keyup(function () {
       text = $(this).val();
       apiurl = $("#apiurl").val();
       render_string = $("#renderstring").val();
       if($("#refid").length)
            refid = $("#refid").val();
        else
            refid = -1;

       send_api_request(apiurl,{ 'q': text, 'refid':refid}, function(data) {render_list('#item_list tbody', data, render_string, true);});
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

       send_api_request(apiurl,{ 'q': text, 'page': page, 'refid': refid}, function(data) {render_list('#item_list tbody', data, render_string, false);});
    });

});
