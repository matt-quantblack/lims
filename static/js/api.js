$(function () {

    function render_dd_list(target, data) {
        $(target).empty();
        $(target).append($('<option>', {value: null, text: "---------"}));
        $.each(data, function (index, item) {
            $(target).append($('<option>', {value: item.id, text: item.name}));
            });
    }

    function render_tr_list(target, data, should_clear_list) {

        if(should_clear_list)
            $(target).empty();

        $.each(data.data, function (index, item) {
          onclick_func = "window.location.href='sample/" + item.id + "'";
          html = '<tr id="sampleid' + item.id +'" onclick="' + onclick_func + '"><td>' + item.id +
              '</td><td>' + item.client + '</td><td>' +
              item.clientref +'</td><td>' + item.batch + '</td><td>' + item.name + '</td><td></td></tr>';

          $(target).append($(html));

        });

        if(!data.more)
            $(".more-pages").hide()
    }

    function send_api_request(url, data, target, renderer, should_clear_list)
    {
        $.ajax({
        url: url,
        data: data,
        dataType: 'json',
        success: function (data) {
          if (data) {
              renderer(target, data, should_clear_list);
          }
        }
      });
    }

    $(".search-samples-input").keyup(function () {
       text = $(this).val();
       send_api_request("/api/searchsamples",{ 'q': text}, '#sample_list tbody', render_tr_list, true);
    });

    $(".search-samples-more").click(function () {
       text = $(this).val();
       page = $(this).attr('page');
       $(this).attr('page', parseInt(page)+1);
       send_api_request("/api/searchsamples",{ 'q': text, 'page': page}, '#sample_list tbody', render_tr_list, false);
    });


    $("#id_client").change(function () {
       id = $(this).val();
       send_api_request("/api/linkednotifcationgroups",{ 'client_id': id}, '#id_notificationgroup', render_dd_list);
    });

    //page loads for lists
    if($(".search-samples-input").length)
        send_api_request("/api/searchsamples",{ 'q': '', 'page': 1}, '#sample_list tbody', render_tr_list, true);
});