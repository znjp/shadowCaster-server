var curCell = -1;
var celltds = new Array(width*height);
var backColors = new Array(width*height);
var moveArr = new Array();
var prevClick = -1;
var curMoves = 0;

function createTd(idx) {
	celltds[idx] = document.createElement('td');
	celltds[idx].id = "c" + idx;
	celltds[idx].style.fontSize = "24pt";
	celltds[idx].style.height = "3.5em";
	celltds[idx].style.width = "3.5em";
	celltds[idx].style.border = "1px solid black";
	celltds[idx].style.textAlign = "center";
	celltds[idx].onmouseover = mouseOver;
	celltds[idx].onmouseout = mouseOut;
	celltds[idx].onmousedown = mouseClick;
	celltds[idx].onselectstart = function(){return false};
	celltds[idx].onmouseup = function(){return false};
	celltds[idx].innerHTML = "&nbsp;";

	if (puzzle.charAt(idx) == '#') {
		celltds[idx].style.backgroundColor = "#666";
		backColors[idx] = "#666";
	} else {
		celltds[idx].style.backgroundColor = "red";
		backColors[idx] = "red";
	}
}

// create the table with all the cells
function initLightsOutGrid() {
	var mydiv = document.getElementById('contain');
	var tbl = document.createElement('table');
	var tbody = document.createElement('tbody');

	for (var i = 0; i < height; i++) {
		var newtr = document.createElement('tr');
		for (var j = 0; j < width; j++) {
			createTd(i*width+j);
			newtr.appendChild(celltds[i*width+j]);
		}
		tbody.appendChild(newtr);
	}
	tbl.appendChild(tbody);
	mydiv.appendChild(tbl);

	//initAfterGrid();
}

function getEventId(e) {
	var targ;
	if (!e) var e = window.event;
	if (e.target) targ = e.target;
	else if (e.srcElement) targ = e.srcElement;
	if (targ.nodeType == 3) targ = targ.parentNode;
	return parseInt(targ.id.substring(1));
}

function mouseOver(e) {
	var idx = getEventId(e);
	curCell = idx;
}

function mouseOut(e) {
	var idx = getEventId(e);
	curCell = -1;
}

function toggleState(idx) {
	var ch;
	if (idx < 0) return false;
	if (idx >= width*height) return false;
	if (curpuz.charAt(idx) == ' ') {
		backColors[idx] = "#666";
		ch = '#';
	} else {
		backColors[idx] = "red";
		ch = ' ';
	}
	celltds[idx].style.backgroundColor = backColors[idx];
	curpuz = curpuz.substr(0, idx) + ch + curpuz.substr(idx+1);

	return curpuz.indexOf(' ') == -1;
}

function mouseClick(e) {
	var idx = getEventId(e);
	if (curCell != idx) return true;
	if (idx == prevClick) {
		curMoves--;
		prevClick = -1;
	} else {
		moveArr[curMoves++] = idx;
		prevClick = idx;
	}
	if (idx >= width) toggleState(idx-width);
	if (idx%width >= 1) toggleState(idx-1);
	if (idx%width <= width-2) toggleState(idx+1);
	if (idx+width < height*width) toggleState(idx+width);
	if (toggleState(idx)) {
		//puzzleDone();
        //alert("Congratulations!");
        //c03144f689169c6f829f920613285ca58a4ab9bd
        document.location = "/release?e=884fd191a2f3809cdf2fd57843571f5e95f6b605";

	}
	return false;
}


