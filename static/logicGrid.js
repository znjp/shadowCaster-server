boardSetup = [null, null, null, null, null, null, null, null, null, null, null, null,null, null, null, null];

$("td").click(function() {
 // console.log(boardSetup);
  var currentClasses = ($(this).attr("class")).split(' ');
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
  clrBoard();
  console.log(boardSetup);
});

function cleanBoard() {
  console.log('foo')
  trueLoc = [];
  for (var i = 0; i < boardSetup.length; i++) {
    if (boardSetup[i]) {
	trueLoc.push(i);
    } else {
	boardSetup[i] = null;
    }
  }
  console.log('truth: ' + trueLoc);
  for (var j = 0; j < trueLoc.length; j++) {
	var col = trueLoc[j] % 4;
	var row = (trueLoc[j] - col) / 4;
	for (var i = 0; i < 4; i++) {
        	if(4*i+col != 4*row+col){
			console.log('row: ' +row)
                        console.log('col: ' + col);
                	boardSetup[4*i+col] = false;
       	 	} else if (4*i+col == 4*row+col) {
                	boardSetup[4*i+col] = true;
        	}
 	 }
  	for (var i = 0; i < 4; i++) {
		console.log('vertical');
        	console.log('row: ' +row)
                console.log('col: ' + col);
        	if(4*row+i != 4*row+col){
			console.log('row: ' +row)
                        console.log('col: ' + col);
                	boardSetup[4*row+i] = false;
        	} else if (4*row+i == 4*row+col) {
               	 	boardSetup[4*row+i] = true;
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
		}
	}
}
