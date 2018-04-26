switches = [];
for (var i = 0; i < 8; i++) {
  switches.push(false);
}

function toggle(binNum) {
  var btn = $('#' + binNum)
  btn.toggleClass('on')
  btn.toggleClass('off')
  switches[binNum] = !switches[binNum];
}

document.getElementById("0").onclick = function () {
  toggle(0)
};
document.getElementById("1").onclick = function () {
  toggle(1)
};
document.getElementById("2").onclick = function () {
  toggle(2)
};
document.getElementById("3").onclick = function () {
  toggle(3)
};
document.getElementById("4").onclick = function () {
  toggle(4)
};
document.getElementById("5").onclick = function () {
  toggle(5)
};
document.getElementById("6").onclick = function () {
  toggle(6)
};
document.getElementById("7").onclick = function () {
  toggle(7)
};

var windowWidth = window.innerWidth ||
  document.documentElement.clientWidth ||
  document.body.clientWidth;

var windowHeight = window.innerHeight ||
  document.documentElement.clientHeight ||
  document.body.clientHeight;

function preload() {
  orImg = loadImage('/static/or.png');
  norImg = loadImage('/static/nor.png');
  andImg = loadImage('/static/and.png');
  xnorImg = loadImage('/static/xnor.png');
  xorImg = loadImage('/static/xor.png');
}

function setup() {
  if (windowWidth < 500) {
    canvas = createCanvas(windowWidth * 0.95, windowHeight * 0.75);
  } else {
    canvas = createCanvas(windowWidth * 0.6, windowHeight * 0.8);
  }
  //var canvas = createCanvas(windowWidth * 0.8, windowHeight * 0.8);
  canvas.parent('gameArea');
  frameRate(20); //sets rate of draw to 20 calls per second instead of 60
  background(0);
}

function draw() {
  background(0);
  var ab = switches[0] && switches[1]
  var cd = switches[2] || switches[3]
  var abcd = ab ^ cd
  var ef = switches[4] ^ switches[5]
  var gh = !(switches[6] ^ switches[7])
  var efgh = !(ef || gh)
  var abcdefgh = abcd && efgh
  push();
  translate(0, -height * 11 / 67);
  scale(1, 1.196)
  if (abcdefgh) {
    drawLines(ab, cd, ef, gh, abcd, efgh, abcdefgh);
    drawGates(ab, cd, ef, gh, abcd, efgh, abcdefgh);
    document.location = "/release?e=0ed3b34226a607d9e5d0ac5c9aa8339b6ad18bbb";
  } else {
    drawLines(false, false, false, false, false, false, false);
    drawGates(false, false, false, false, false, false, false);
  }
  pop();
}

function drawLines(bool, bool1, bool2, bool3, bool4, bool5, bool6) {
  xPos = width / 9;
  yPos = height * 11 / 67;
  for (var i = 0; i < switches.length; i++) {
    strokeWeight(width / 128);
    if (bool6) {
      stroke(clrBoolean(switches[i]));
    } else {
      stroke(245);
    }
    strokeJoin(MITER);
    beginShape();
    noFill();
    vertex(xPos, (12 / 67) * height);
    vertex(xPos, (1 / 3) * height);
    if (i % 2 === 0) {
      vertex(xPos + width / 18, height / 3)
    } else {
      vertex(xPos - width / 18, height / 3)
    }
    endShape();
    xPos += width / 9;
  }
  noFill();
  strokeWeight(width / 128);
  if (bool6) {
    stroke(clrBoolean(bool));
  } else {
    stroke(245);
  }
  strokeJoin(MITER);
  beginShape();
  vertex(width / 6, (1 / 3 + 1 / 32) * height);
  vertex(width / 6, (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  vertex(width * (5 / 18), (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  endShape();

  if (bool6) {
    stroke(clrBoolean(bool1));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 7 / 18, (1 / 3 + 1 / 32) * height);
  vertex(width * 7 / 18, (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  vertex(width * (5 / 18), (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  endShape();

  if (bool6) {
    stroke(clrBoolean(bool2));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 11 / 18, (1 / 3 + 1 / 32) * height);
  vertex(width * 11 / 18, (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  vertex(width * (13 / 18), (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  endShape();

  if (bool6) {
    stroke(clrBoolean(bool3));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 15 / 18, (1 / 3 + 1 / 32) * height);
  vertex(width * 15 / 18, (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  vertex(width * (13 / 18), (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  endShape();

  if (bool6) {
    stroke(clrBoolean(bool4));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 5 / 18, (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  vertex(width * 5 / 18, (1 / 3 + (2 / 3) * (2 / 4) + 1 / 32) * height);
  vertex(width * (5 / 18 + 1 / 4), (1 / 3 + (2 / 3) * (2 / 4) + 1 / 32) * height);
  endShape();

  if (bool6) {
    stroke(clrBoolean(bool5));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 13 / 18, (1 / 3 + (2 / 3) * (1 / 4) + 1 / 32) * height);
  vertex(width * 13 / 18, (1 / 3 + (2 / 3) * (2 / 4) + 1 / 32) * height);
  vertex(width * (13 / 18 - 1 / 4), (1 / 3 + (2 / 3) * (2 / 4) + 1 / 32) * height);
  endShape();

  if (bool6) {
    stroke(clrBoolean(bool6));
  } else {
    stroke(245);
  }
  line(width / 2, (1 / 3 + (2 / 3) * (2 / 4) + 1 / 32) * height, width / 2, (1 / 3 + (2 / 3) * (3 / 4) + 1 / 32) * height)
}


function checkLogic() {
  var ab = switches[0] && switches[1]
  var cd = switches[2] || switches[3]
  var abcd = ab ^ cd
  var ef = switches[4] ^ switches[5]
  var gh = !(switches[6] ^ switches[7])
  var efgh = !(ef || gh)
  var abcdefgh = abcd && efgh
  return abcdefgh
}

function drawGate(label, x, y, boolean) {
  push();
  translate(x, y);
  if (label == "XOR") {
    image(xorImg, -xorImg.width / 2, -xorImg.height / 3);
  } else if (label == "OR") {
    image(orImg, -orImg.width / 2, -orImg.height / 3);
  } else if (label == "AND") {
    image(andImg, -andImg.width / 2, -andImg.height / 3);
  } else if (label == "XNOR") {
    image(xnorImg, -xnorImg.width / 2, -xnorImg.height / 3);
  } else if (label == "NOR") {
    image(norImg, -norImg.width / 2, -norImg.height / 3);
  } else {
    fill(clrBoolean(boolean));
    noStroke();
    rect(-width * 3 / 36, 0, width * 3 / 18, height / 16);
    fill(255)
    textFont('Quantico');
    textAlign(CENTER, CENTER);
    text('releaseLight()', -width * 3 / 36, 0, width * 3 / 18, height / 16);
  }

  pop();
}

function drawGates(bool, bool1, bool2, bool3, bool4, bool5, bool6) {
  drawGate('AND', width / 6, (1 / 3) * height, bool)
  drawGate('OR', width * 7 / 18, (1 / 3) * height, bool1)
  drawGate('XOR', width * 11 / 18, (1 / 3) * height, bool2)
  drawGate('XNOR', width * 15 / 18, (1 / 3) * height, bool3)
  drawGate('XOR', width * 5 / 18, (1 / 3 + (2 / 3) * (1 / 4)) * height, bool4)
  drawGate('NOR', width * 13 / 18, (1 / 3 + (2 / 3) * (1 / 4)) * height, bool5)
  drawGate('AND', width * 9 / 18, (1 / 3 + (2 / 3) * (2 / 4)) * height, bool6)
  drawGate('', width / 2, (1 / 3 + (2 / 3) * (3 / 4)) * height, bool6)
}

function randBoolean() {
  if (Math.round(Math.random()) === 0) {
    return false;
  } else {
    return true;
  }
}

function clrBoolean(boolean) {
  if (boolean) {
    return color(65, 222, 65)
  } else {
    return color(218, 46, 46)
  }
}