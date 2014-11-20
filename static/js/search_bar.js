var substringMatcher = function(strs) {
  return function findMatches(q, cb) {
    var matches, substringRegex;

    // an array that will be populated with substring matches
    matches = [];

    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        // the typeahead jQuery plugin expects suggestions to a
        // JavaScript object, refer to typeahead docs for more info
        matches.push({ value: str });
      }
    });

    cb(matches);
  };
};

var livres = [];
function set_search_bar(search_name, insert_after){
    $(search_name).attr('autocomplete', 'off');
    var $autocomplete = $("<ul id='autocomplete'></ul>").hide().insertAfter(insert_after);
    var selectedItem = null;

    var populateSearchField = function(escape){
        $(search_name).val($autocomplete.find('li').eq(selectedItem).text());
        if(escape){
            setSelectedItem(null);
        }
    }
    var setSelectedItem = function(item){
        selectedItem = item;
        if (selectedItem === null){
            $autocomplete.hide();
            return;
        }
        else if(selectedItem < 0){
            selectedItem = 0;
        }
        else if(selectedItem >= $autocomplete.find('li').length){
            selectedItem = $autocomplete.find('li').length - 1;
        }
        $autocomplete.find('li').removeClass('selected').eq(selectedItem).addClass('selected');
        $autocomplete.show();
    }
    $(search_name).keypress(function(event){
        if(event.keyCode == 13 && selectedItem !== null){
            populateSearchField(true);
        }
    });
    $(search_name).keyup(function(event){
        if(event.keyCode > 40 || event.keyCode == 8){
            $.ajax({
                    url: "http://completion.amazon.co.uk/search/complete",
                    type: "GET",
                    cache: false,
                    dataType: "jsonp",
                    success: function (data) {
                        console.log(data[1]);
                        if(data[1].length){
                            $autocomplete.empty();
                            $.each(data[1], function(index, term) {
                                $('<li></li>').text(term).appendTo($autocomplete)
                                .mouseover(function(){
                                    setSelectedItem(index);
                                })
                                .click(function(){
                                    $(search_name).val(term);
                                    $autocomplete.hide();
                                });
                            });
                            var len = $autocomplete.find('li').length;
                            $($autocomplete.find('li')[0]).addClass("first_list");
                            $($autocomplete.find('li')[len-1]).addClass("last_list");

                            setSelectedItem(0);
                        }
                        else{
                            setSelectedItem(null);   
                        }
                    },
                    data: {
                        q: $(search_name).val(),
                        "search-alias": "stripbooks",
                        mkt: "5",
                    }
            });
        }
        else if (event.keyCode == 38 && selectedItem !== null){
            //haut
            setSelectedItem(selectedItem - 1);
            populateSearchField(false);
        }
        else if (event.keyCode == 40 && selectedItem !== null){
            //haut
            setSelectedItem(selectedItem + 1);
            populateSearchField(false);
        }
        else if (event.keyCode == 27 && selectedItem !== null){
            //echap
            setSelectedItem(null);
        }
    });
    $(search_name).blur(function(event){
        setTimeout(function(){
            setSelectedItem(null);
        }, 250);
    })
}