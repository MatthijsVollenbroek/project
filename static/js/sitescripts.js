    // variabele die onthoudt of je al gelikete of gedislikete hebt
    var previous = null;

  function postlike(postid) {
    $.ajax({
      url: "/like?postid="+ postid,
      type: 'get',
      success: function(data) {
      if (data.success)
        {
          // like counter verhogen met 1
          $('#likes'+postid).text(parseInt($('#likes'+postid).text()) + 1);

          // als je post liked die je al gedisliked hebt dan counter van dislike verlagen met 1
          if (previous == 'dis'){
            $('#dislikes'+postid).text(parseInt($('#dislikes'+postid).text()) - 1);
          }
          // onthoud de like
          previous = 'like';
        }
      }

    });
  }
  function postdislike(postid) {
    $.ajax({
      url: "/dislike?postid="+ postid,
      type: "get",
      success: function(data) {
        if (data.success)
        {
          // dislike counter verhogen met 1
          $('#dislikes'+postid).text(parseInt($('#dislikes'+postid).text()) + 1);

          //als je post disliked die je al geliked hebt dan counter van like verlagen met 1
          if (previous == 'like'){
            $('#likes'+postid).text(parseInt($('#likes'+postid).text()) - 1);
          }
          // onthoud de dislike
          previous = 'dis';

        }
      }

    });
  }


