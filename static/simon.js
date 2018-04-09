// isMobile and the condition of the following if statement is from https://www.mattcromwell.com/detecting-mobile-devices-javascript/

var isMobile = {
  Android: function () {
    return navigator.userAgent.match(/Android/i);
  },
  BlackBerry: function () {
    return navigator.userAgent.match(/BlackBerry/i);
  },
  iOS: function () {
    return navigator.userAgent.match(/iPhone|iPad|iPod/i);
  },
  Opera: function () {
    return navigator.userAgent.match(/Opera Mini/i);
  },
  Windows: function () {
    return navigator.userAgent.match(/IEMobile/i);
  },
  any: function () {
    return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
  }
};

$('#blue').click(function () {
  if (isMobile.any()) {
    $(this).addClass('mobile');
    setTimeout(function () {
      $('#blue').removeClass('mobile');
    }, 105);
  }
})


$('#red').click(function () {
  if (isMobile.any()) {
    $(this).addClass('mobile');
    setTimeout(function () {
      $('#red').removeClass('mobile');
    }, 105);
  }
})

$('#green').click(function () {
  if (isMobile.any()) {
    $(this).addClass('mobile');
    setTimeout(function () {
      $('#green').removeClass('mobile');
    }, 105);
  }
})

$('#dark').click(function () {
  if (isMobile.any()) {
    $(this).addClass('mobile');
    setTimeout(function () {
      $('#dark').removeClass('mobile');
    }, 105);
  }
})

// Simon game from: https://codepen.io/mrkaluzny/full/pbVxxd

var game = {
  count: 0,
  possibilities: ['#green', '#blue', '#red', '#dark'],
  currentGame: [],
  player: [],
  strict: false,
}

function clearGame() {
  game.currentGame = [];
  game.count = 0;
  addCount();
}

function newGame() {
  clearGame();
}


function showMoves() {
  var i = 0;
  var moves = setInterval(function () {
    playGame(game.currentGame[i]);
    i++;
    if (i >= game.currentGame.length) {
      clearInterval(moves);
    }
  }, 600)

  clearPlayer();
}

function playGame(field) {

  $(field).addClass('hover');
  //sound(field);
  setTimeout(function () {
    $(field).removeClass('hover');
  }, 300);

}

function clearPlayer() {
  game.player = [];
}

function addToPlayer(id) {
  var field = "#" + id
  game.player.push(field);
  playerTurn(field);
}

function playerTurn(x) {
  if (game.player[game.player.length - 1] !== game.currentGame[game.player.length - 1]) {
    if (game.strict) {
      //alert('Try again! ...From scratch!');
      newGame();
    } else {
      //alert('Wrong move! Try again!');
      showMoves();
    }
  } else {
    var check = game.player.length === game.currentGame.length;
    if (check) {
      if (game.count == 10) {
        //alert('You won! Congrats.');
        document.location = "/release?e=0ead1af0d93152471770c3095c0489cb6e8a70c5";
      } else {
        //alert('Next round!');
        nextLevel();
      }
    }
  }
}

function nextLevel() {
  addCount();
}

function generateMove() {
  game.currentGame.push(game.possibilities[(Math.floor(Math.random() * 4))]);
  showMoves();
}

function addCount() {
  game.count++;
  //document.getElementById('clickNumber').innerHTML = game.count;

  $('#clickNumber').addClass('animated fadeOutDown');

  setTimeout(function () {
    $('#clickNumber').removeClass('fadeOutDown').html(game.count).addClass('fadeInDown');
  }, 200);

  generateMove();
}

newGame();