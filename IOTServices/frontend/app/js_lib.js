/*
 * Javascript file to implement client side usability for 
 * Operating Systems Desing exercises.
 */
 var api_server_address = "http://34.91.117.155:5001/"

 var get_current_sensor_data = function(){
    $.getJSON( api_server_address+"device_state", function( data ) {
        $.each(data, function( index, item ) {
            
            console.log(item.room, item.type, item.value )
            
            
          $("#"+item.room).data(item.type, item.value)
      });
    });
}

var draw_rooms = function(){
    $("#rooms").empty()
    var room_index = 1;
    for (var i = 0; i < 8; i++) {
        $("#rooms").append("<tr id='floor"+i+"'></tr>")
        for (var j = 0; j < 5; j++) {
            $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class='room_cell'\
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            room_index++
        }
    }
}

$("#persiana").change(function(){
    var value = $(this).val()
    var estado_per = '';
    if (value==0){
        estado_per='OPEN';
    }else{
        estado_per='CLOSE';
    }
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"blind",
            "value":estado_per,
        }),
        contentType: 'application/json'
    });
})

$("#luz").change(function(){
    var value = $(this).val()
    var estado_luz = '';
    if (value==1){
        estado_luz='OFF';
    }else{
        estado_luz='ON';
    }
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"indoor_light",
            "value":estado_luz,
        }),
        contentType: 'application/json'
    });
})

$("#apagar").on("click", function(){
    
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"SHUTDOWN",
            "value":"OFF",
        }),
        contentType: 'application/json'
    });
})

$("#rooms").on("click", "td", function() {
    $("#room_id").text($( this ).attr("id") || "");
    $("#temperature_value").text($( this ).data("temperature") || "");
    $("#luz_tag").text($( this ).data("indoor_light") );
    $("#persiana_tag").text($( this ).data("blind") );
    $("#presence_value").text($( this ).data("state"));
});

draw_rooms()
setInterval(get_current_sensor_data,3000)

