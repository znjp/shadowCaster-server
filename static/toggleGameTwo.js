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
  nandImg = loadImage('/static/nand.png');
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
  switches = [];
  for (var i = 0; i < 10; i++) {
    switches.push(false);
  }
  background(0);
}

function draw() {
  background(0);
  a = (switches[0] ^ switches[1]);
  b = (switches[2] ^ switches[3]);
  c = (switches[4] || switches[5]);
  d = switches[6] && switches[7];

  g = !(c ^ d);
  f = b && c;
  e = a || b;
  h = a || e;

  k = !(f || g)
  j = e && f
  l = g ^ (d)

  m = ((switches[8] && j) ^ h)
  n = !((switches[8] && j) && (switches[9] && k))
  o = (switches[9] && k) && l

  final = m && n && o
  if (final){
    document.location = "/release?e=ccd5f517154e95c4964c86a92a58dea50d17c33e";
  }

  drawLines();
  drawGates();
  drawSwitches();
}

function drawSwitches() {
  var xPos = width / 9;
  var yPos = (1 / 4 - (3 / 4) * (1 / 6)) * height;
  for (var i = 0; i < 8; i++) {
    drawSwitch(xPos, yPos, switches[i]);
    xPos += width / 9;
  }
  drawToggle(width * 7 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height, j, switches[8]);
  drawToggle(width * 11 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height, k, switches[9]);
}

function drawToggle(x, y, powerFlowing, toggleBoolean) {
  push();
  stroke(60)
  strokeWeight(width * 0.75 / 64)
  translate(x, y)
  fill(100)
  rect(-width * 3 / 36, 0, width * 3 / 18, height * 1.5 / 32)

  if (powerFlowing) {
    fill(clrBoolean(toggleBoolean))
  } else {
    fill(180)
  }
  if (toggleBoolean) {
    rect(width * 1 / 36, 0, width * 1 / 18, height * 1.5 / 32)
  } else {
    rect(-width * 3 / 36, 0, width * 1 / 18, height * 1.5 / 32)
  }
  pop();
}

function drawLines() {
  xPos = width / 9;
  yPos = height / 8;
  noFill();
  for (var i = 0; i < 8; i++) {
    strokeWeight(width / 128);
    if (final) {
      stroke(clrBoolean(switches[i]));
    } else {
      stroke(245);
    }
    strokeJoin(MITER);
    noFill();
    beginShape();
    vertex(xPos, (12 / 67) * height);
    vertex(xPos, (1 / 4) * height);
    if (i % 2 === 0) {
      vertex(xPos + width / 18, height / 4)
    } else {
      vertex(xPos - width / 18, height / 4)
    }
    endShape();
    xPos += width / 9;
  }
  strokeJoin(MITER);
  strokeWeight(width / 128);
  if (final) {
    stroke(clrBoolean(a));
  } else {
    stroke(245);
  }
  // a is correct
  beginShape();
  vertex(width / 6, (1 / 4) * height);
  vertex(width / 6, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * (5 / 18), (1 / 4 + (3 / 4) * (1 / 6)) * height);
  endShape();
  beginShape();
  vertex(width / 6, (1 / 4) * height);
  vertex(width / 6, (1 / 4 + (3 / 4) * (2 / 6)) * height)
  endShape();

  if (final) {
    stroke(clrBoolean(b));
  } else {
    stroke(245);
  }
  //b is correct
  beginShape();
  vertex(width * 7 / 18, (1 / 4) * height);
  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * (5 / 18), (1 / 4 + (3 / 4) * (1 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 7 / 18, (1 / 4) * height);
  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height)
  vertex(width * 9 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height)
  endShape();

  if (final) {
    stroke(clrBoolean(c));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 11 / 18, (1 / 4) * height);
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * (9 / 18), (1 / 4 + (3 / 4) * (1 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 11 / 18, (1 / 4) * height);
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height)
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height)
  endShape();

  if (final) {
    stroke(clrBoolean(d));
  } else {
    stroke(245)
  }

  beginShape();
  vertex(width * 5 / 6, (1 / 4) * height);
  vertex(width * 5 / 6, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * (13 / 18), (1 / 4 + (3 / 4) * (1 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 5 / 6, (1 / 4) * height);
  vertex(width * 5 / 6, (1 / 4 + (3 / 4) * (2 / 6)) * height)
  endShape();

  if (final) {
    stroke(clrBoolean(h));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 3 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * 3 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (5 / 18), (1 / 4 + (3 / 4) * (4 / 6)) * height);
  endShape();
  if (final) {
    stroke(clrBoolean(l));
  } else {
    stroke(245);
  }

  beginShape();
  vertex(width * 5 / 6, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * 5 / 6, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (13 / 18), (1 / 4 + (3 / 4) * (4 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(e));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (11 / 18), (1 / 4 + (3 / 4) * (2 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (15 / 18), (1 / 4 + (3 / 4) * (2 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(h));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 9 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * 9 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (11 / 18), (1 / 4 + (3 / 4) * (2 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 9 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * 9 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (7 / 18), (1 / 4 + (3 / 4) * (2 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(j));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 5 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * 5 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (3 / 18), (1 / 4 + (3 / 4) * (2 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 5 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height);
  vertex(width * 5 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (7 / 18), (1 / 4 + (3 / 4) * (2 / 6)) * height);
  endShape();

  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * (7 / 18), (1 / 4 + (3 / 4) * (3 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(k));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height);
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(m));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 5 / 18, (1 / 4 + (3 / 4) * (4 / 6) + 1 / 64) * height);
  vertex(width * 5 / 18, (1 / 4 + (3 / 4) * (5 / 6) + 1 / 64) * height);
  vertex(width * (9 / 18), (1 / 4 + (3 / 4) * (5 / 6) + 1 / 64) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(switches[8] && j))
  } else {
    stroke(245);
  }

  beginShape();
  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height);
  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (9 / 18), (1 / 4 + (3 / 4) * (4 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height);
  vertex(width * 7 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (5 / 18), (1 / 4 + (3 / 4) * (4 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(switches[9] && k))
  } else {
    stroke(245);
  }

  beginShape();
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height);
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (13 / 18), (1 / 4 + (3 / 4) * (4 / 6)) * height);
  endShape();
  beginShape();
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (3 / 6)) * height);
  vertex(width * 11 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (9 / 18), (1 / 4 + (3 / 4) * (4 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(n));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 9 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height);
  vertex(width * (9 / 18), (1 / 4 + (3 / 4) * (5 / 6)) * height);
  endShape();

  if (final) {
    stroke(clrBoolean(o));
  } else {
    stroke(245);
  }
  beginShape();
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (4 / 6) + 1 / 64) * height);
  vertex(width * 13 / 18, (1 / 4 + (3 / 4) * (5 / 6) + 1 / 64) * height);
  vertex(width * (9 / 18), (1 / 4 + (3 / 4) * (5 / 6) + 1 / 64) * height);
  endShape();
}

function drawSwitch(x, y, boolean) {
  push();
  translate(x, y);
  scale(1, 3 / 16);
  fill(245);
  noStroke();
  fill(clrBoolean(boolean))
  rect(-width / 36, 0, width / 18, height / 4);
  stroke(245);
  strokeWeight(5);
  arc(0, 0, width / 18, height / 8, PI, 2 * PI);
  arc(0, height / 4, width / 18, height / 8, 0, PI);
  line(-width / 36 - 0.5, 0, -width / 36 - 0.5, height / 4);
  line(width / 36 - 0.5, 0, width / 36 - 0.5, height / 4);
  pop();
}

function touchStarted() {
  console.log('x: ' + mouseX);
  console.log('width: ' + width);
  console.log('y: ' + mouseY);
  console.log('height: ' + height);
  if (mouseY > height * 3.5 / 32 && mouseY < height * 6 / 32) {
    for (var i = 0; i < switches.length; i++) {
      if (mouseX > width * ((1 + i) / 9) - (1 / 36) * width && mouseX < width * ((1 + i) / 9) + (1 / 36) * width) {
        switches[i] = !switches[i];
      }
    }
  } else if (mouseY > height * 5 / 8 && mouseY < height * 43 / 64) {
    if (mouseX > width * (7 / 18 - 3 / 36) && mouseX < width * (7 / 18 + 3 / 36)) {
      switches[8] = !switches[8]
    } else if (mouseX > width * ((11 / 18) - (3 / 36)) && mouseX < width * (11 / 18 + 3 / 36)) {
      switches[9] = !switches[9]
    }
  }
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
  } else if (label == "NAND") {
    image(nandImg, -nandImg.width / 2, -nandImg.height / 3);
  } else {
    fill(clrBoolean(boolean));
    noStroke();
    rect(-width * 3 / 36, 0, width * 3 / 18, height / 16);
    fill(255);
    textFont('Quantico');
    textAlign(CENTER,CENTER);
    text('releaseLight()', -width * 3 / 36, 0, width * 3 / 18, height / 16);
  }
  pop();
}

function drawGates() {
  drawGate('XOR', width * 3 / 18, (1 / 4) * height, d)
  drawGate('XOR', width * 7 / 18, (1 / 4) * height, c)
  drawGate('OR', width * 11 / 18, (1 / 4) * height, b)
  drawGate('AND', width * 15 / 18, (1 / 4) * height, a)

  drawGate('XNOR', width * 13 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height, e)
  drawGate('AND', width * 9 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height, f)
  drawGate('OR', width * 5 / 18, (1 / 4 + (3 / 4) * (1 / 6)) * height, g)

  drawGate('OR', width * 3 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height, l)
  drawGate('AND', width * 7 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height, k)
  drawGate('NOR', width * 11 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height, j)
  drawGate('XOR', width * 15 / 18, (1 / 4 + (3 / 4) * (2 / 6)) * height, h)

  // two switches are drawn at this height

  drawGate('XOR', width * 5 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height, m)
  drawGate('NAND', width * 9 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height, n)
  drawGate('AND', width * 13 / 18, (1 / 4 + (3 / 4) * (4 / 6)) * height, o)


  drawGate('', width / 2, (1 / 4 + (3 / 4) * (5 / 6)) * height, final)


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