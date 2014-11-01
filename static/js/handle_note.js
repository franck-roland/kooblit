
function send_note(){
    $.ajax({
        url: $(this).attr('action'),
        type: "GET",
        cache: false,
        success: function(data){
            location.reload();
        },
        data: {
            "note": $(this).attr('note'),
        }
      });
}


