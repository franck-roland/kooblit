var background_colors = ["#F5A9F2", "#F7BE81", "#BCF5A9", "#A9F5F2", "#F2F5A9"];
// rose, orange, vert, bleu, jaune
var owl_color = ["green", "marine_blue", "red", "marine_blue", "violet"]

function colorize (position, element) {
    var owl_file = "img/logo/owl_"+owl_color[position%owl_color.length]+".png";
    var background_color = background_colors[position%owl_color.length];
    $(element).css("background", background_color);
    $(element).find('img').attr("src","/static/"+owl_file);
}