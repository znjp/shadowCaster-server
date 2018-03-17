var goal1 = Math.round(Math.random() * 204) + 51;
var goal2 = Math.round(Math.random() * 204) + 51;
var goal3 = Math.round(Math.random() * 204) + 51;

document.getElementById('mainHeading').innerHTML = goal1 + " ^ 0" + goal2.toString(8) + ' | ~0x' + goal3.toString(16) + ' & 0b11111111';

//get window size
var windowWidth = window.innerWidth ||
  document.documentElement.clientWidth ||
  document.body.clientWidth;

var windowHeight = window.innerHeight ||
  document.documentElement.clientHeight ||
  document.body.clientHeight;

function setup() {
  if (windowWidth < 500) {
    canvas = createCanvas(windowWidth * 0.95, windowHeight * 0.75);
  } else {
    canvas = createCanvas(windowWidth * 0.6, windowHeight * 0.8);
  }
  canvas.parent('gameArea');
  frameRate(20); //sets rate of draw to 20 calls per second instead of 60
  var currentNum = 0;
  switches = [];
  for (var i = 0; i < 8; i++) {
    switches.push(false);
  }
}

function draw() {
  background(20);
  textSize(75);
  var xPos = width / 9;
  var yPos = height / 2;
  for (var i = 0; i < switches.length; i++) {
    noStroke();
    fill(255);
    if (switches[i]) {
      text('1', xPos - 47 / 2, yPos - height / 6);
    } else {
      text('0', xPos - 47 / 2, yPos - height / 6);
    }
    //ellipse((width * (1 + i)) / 9, height / 2, width / 18, height / 8)
    drawSwitch(xPos, yPos + height / 32, switches[i]);
    xPos += width / 9;
  }
  currentNum = 0
  for (var i = 0; i < switches.length; i++) {
    if (switches[switches.length - 1 - i]) {
      currentNum += Math.pow(2, i);
    }
  }
  if (currentNum == (goal1 ^ goal2 | ~goal3 & 255)){
      document.location = "/release?e=14265e37fd16904ee3d4a306ff25016de9181eb8";
  }
}

function drawSwitch(x, y, boolean) {
  if (boolean) {
    fill(65, 222, 65);
  } else {
    fill(218, 46, 46);
  }
  rect(x - width / 36, y, width / 18, height / 4);
  stroke(245);
  strokeWeight(5);
  arc(x, y, width / 18, height / 8, PI, 2 * PI);
  arc(x, y + height / 4, width / 18, height / 8, 0, PI);
  line(x - width / 36 - 0.5, y, x - width / 36 - 0.5, y + height / 4);
  line(x + width / 36 - 0.5, y, x + width / 36 - 0.5, y + height / 4);
}

function touchStarted() {
  if (mouseY > height * 17 / 32 && mouseY < height * 29 / 32) {
    for (var i = 0; i < switches.length; i++) {
      if (mouseX > width * (1 + i) / 9 && mouseX < width * (1 + i) / 9 + width / 18) {
        switches[i] = !switches[i];
      }
    }
  }
}