$( document ).ready(function() {
  $(document).foundation();

  //organisation name
  $('#ok').hide();
  $('#nok').hide();
  $('#start_details #name').on('blur', function(evt) {
        var nameToCheck = evt.currentTarget.value;
        $.ajax({ cache: false,
            url: "/check",
            data: { 'name': nameToCheck},
            success: function(data) {
              $('#nok').show();
              $('#start_details #name').focus();
              $('#ok').hide();
            },
            error: function(xhr, textStatus, errorThrown) {
              if(xhr.status==404 || textStatus=='NOT FOUND'){
                  $('#ok').show();
                  $('#nok').hide();
              }
            }
        });
  });

  //directors
  show_hide_invites();
  function show_hide_invites(){

    $('#director_contact table').remove();

    if ($("#director_count").val() && $("#director_count").val() > 0){
     for(i=0; i<$("#director_count").val(); i++){
       $('#director_contact').append("<table id='people-"+i+"'><tr><th><label for='people-"+i+"-fullname'>Name</label></th><td><input id='people-"+i+"-fullname' name='people-"+i+"-fullname' type='text' value=''></td></tr><tr><th><label for='people-"+i+"-position'>Position</label></th><td><input id='people-"+i+"-position' name='people-"+i+"-position' type='text' value=''></td></tr><tr><th><label for='people-"+i+"-phone'>Phone number</label></th><td><input id='people-"+i+"-phone' name='people-"+i+"-phone' type='tel' value=''></td></tr></table>");
     }
      $('#director_contact').show();
    } else {
      $('#director_contact').hide();
    }
  }

  $("#director_count").change(function() {
    show_hide_invites();
  });

  //done
  if ($("#done-pending").length > 0 && $("#done-done").length > 0){
    $("#done-done").hide();
    setTimeout(function() {
      $("#done-done").show();
      $("#done-pending").hide();
      if (navigator.vibrate !== undefined) {
        navigator.vibrate(1000);
      }
    }, 5000);
  }

  //todo list
  $('.todo').on('close.fndtn.alert-box', function(event) {
    var todoId = $(event.currentTarget).attr('id'),
        orgId = $(event.currentTarget).data('org');
    $.ajax({
      url: '/manage/'+orgId+'/todos/'+todoId,
      type: 'DELETE',
      success: function(result) {
          var todoCount = $('div.todo').length;
          if(todoCount == 0){
            $('span.alert').remove();
            $('i.notification').removeClass('notification');
          } else {
            $('span.alert').text(todoCount);
          }
      }
    });
  });

});
