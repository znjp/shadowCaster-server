function timer(callback, delay) {
    var id, started, remaining = delay, running

    this.start = function() {
        running = true
        started = new Date()
        id = setTimeout(callback, remaining)
    }

    this.pause = function() {
        running = false
        clearTimeout(id)
        remaining -= new Date() - started
    }

    this.getTimeLeft = function() {
        if (running) {
            this.pause()
            this.start()
        }

        return remaining
    }

    this.getStateRunning = function() {
        return running
    }

    this.start()
}

boardSetup = [null, null, null, null, null, null, null, null, null, null, null, null,null, null, null, null];
losing = true
$("td").click(function() {
	console.log(losing)
	if (losing === true) {
  		var currentClasses = ($(this).attr("class")).split(' ');
  		if (currentClasses.length > 1) {
  			var row = Number(currentClasses[1][3]);
  			var col = Number(currentClasses[0][3]);
  			if (boardSetup[row*4 + col]) {
				boardSetup[row*4 + col] = null
				truthCorrect(col, row);
  			} else if (boardSetup[row*4 + col] == null) {
				boardSetup[row*4 + col] = true
  			} else if (boardSetup[row*4 + col] === false) {
				boardSetup[row*4 + col] = true
        			truthCorrect(col, row);
  			}	
  			cleanBoard();
  			if (clrBoard() == 4) {
      				if (checkRes()) {
        				document.location = "/release?e=c03144f689169c6f829f920613285ca58a4ab9bd";
      				} else {
					losing = false;
					alert("Incorrect deduction.\r\nYou must pause to let the shadowcasters pass.");
					punish = new timer(function() {
						losing = true;
        					console.log('3 ' + losing);					 
					}, 4000)
					$('#timing').removeClass('hidden');
					//document.getElementById("timing").outerHTML = punish.getTimeLeft()/1000;
					while (punish.getTimeLeft()>0) {
						//$('#timing').text(punish.getTimeLeft()/1000);
						//console.log(punish.getTimeLeft()/1000);
						//console.log(document.getElementById("timing"))
						document.getElementById("timing").innerHTML = punish.getTimeLeft()/1000;
						//console.log(document.getElementById("hidden").outerHTML)
						//console.log(document.getElementById("timing").outerHTML)
					}
					$('#timing').addClass('hidden');
      				}
    			}
  		}
	}	
});

function cleanBoard() {
  trueLoc = [];
  for (var i = 0; i < boardSetup.length; i++) {
    if (boardSetup[i]) {
	trueLoc.push(i);
    } else {
	boardSetup[i] = null;
    }
  }
  for (var j = 0; j < trueLoc.length; j++) {
	var col = trueLoc[j] % 4;
	var row = (trueLoc[j] - col) / 4;
	for (var i = 0; i < 4; i++) {
        	if(4*i+col != 4*row+col){
                	boardSetup[4*i+col] = false;
       	 	}
 	 }
  	for (var i = 0; i < 4; i++) {
        	if(4*row+i != 4*row+col) {
                	boardSetup[4*row+i] = false;
        	}
  	}
  }
}

function truthCorrect(newX, newY){
        for (var i = 0; i < 4; i++) {
                if(4*i+newX != 4*newY+newX){
                        boardSetup[4*i+newX] = null;
                }
         }
        for (var i = 0; i < 4; i++) {
                if(4*newY+i != 4*newY+newX){
                        boardSetup[4*newY+i] = null;
                }
        }

}

function clrBoard() {
  var truthCount = 0;
	for (var i = 0; i < boardSetup.length; i++) {
		var col = i % 4;
	        var row = (i - col) / 4;
		if (boardSetup[i] == null) {
			$('.col' + col.toString() + '.row' + row.toString()).removeClass('selected');
			$('.col' + col.toString() + '.row' + row.toString()).removeClass('deselected');
		} else if (boardSetup[i] == false) {
			$('.col' + col.toString() + '.row' + row.toString()).removeClass('selected');
      $('.col' + col.toString() + '.row' + row.toString()).addClass('deselected');
		} else if (boardSetup[i] == true) {
			$('.col' + col.toString() + '.row' + row.toString()).addClass('selected');
      $('.col' + col.toString() + '.row' + row.toString()).removeClass('deselected');
      truthCount += 1;
    }
	}
  return truthCount
}

function checkRes() {
  return boardSetup[3] && boardSetup[4] && boardSetup[10] && boardSetup[13]
}
