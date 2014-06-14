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
$('.form-control ').typeahead({
  hint: true,
  highlight: true,
  minLength: 3
},
{
  name: 'livres',
  displayKey: function(s){ return s.toString();},
  source: function (request, cb) {
                $.ajax({
                    url: "http://completion.amazon.co.uk/search/complete",
                    type: "GET",
                    cache: false,
                    dataType: "jsonp",
                    success: function (data) {
                        livres = data[1];
                        cb($.makeArray(data[1]));
                    },
                    data: {
                        q: request,
                        "search-alias": "stripbooks",
                        mkt: "5",
                        callback: '?'
                    }
                });
            }
},
{
  name: 'livres_anglais',
  displayKey: function(s){ return s.toString();},
  source: function (request, cb) {
                $.ajax({
                    url: "http://completion.amazon.co.uk/search/complete",
                    type: "GET",
                    cache: false,
                    dataType: "jsonp",
                    success: function (data) {
                        var temp = [];
                        for (var l in data[1]){
                            if (livres.indexOf(data[1][l]) == -1){
                                temp.push(data[1][l]);
                            }
                        }
                        if (!$('.divider').length){
                            $('.tt-dataset-livres').after('<div class="divider"></div>');
                        }
                        cb(temp);
                        
                    },
                    data: {
                        q: request,
                        "search-alias": "english-books",
                        mkt: "5",
                        callback: '?'
                    }
                });
            }
}
);
