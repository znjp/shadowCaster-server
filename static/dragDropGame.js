//get window size
var windowWidth = window.innerWidth ||
  document.documentElement.clientWidth ||
  document.body.clientWidth;

var windowHeight = window.innerHeight ||
  document.documentElement.clientHeight ||
  document.body.clientHeight;

//avoid pesking issues with fullscreen
var canvasWidth = windowWidth * 0.9945;
var canvasHeight = windowHeight * 0.9945;

// each line of code for the drag and dragDropGame should be its own string

if (game == "one"){
  var slot0 = 'def shadowLoop:';
  var slot1 = '   lightLevel = 0';
  var slot2 = '   while True:';
  var slot3 = '      if lightLevel < 100:';
  var slot4 = '         self.releaseLight(10)';
  var slot5 = '       if lightLevel > 100:';
  var slot6 = '         lightLevel = self.acquireLight()';
}else if(game == "two"){
  var slot0 = 'import hashlib';
  var slot1 = 'import os';
  var slot2 = '';
  var slot3 = '#generate a random key';
  var slot4 = 'key = random.getrandbytes(20)';
  var slot5 = '';
  var slot6 = '';
  var slot7 = 'def find_collision():';
  var slot8 = '    preimage = os.urandom(20)';
  var slot9 = '    target = hashlib.sha1(preimage).digest()';
  var slot10 = '    count = 0';
  var slot11 = '    #Compute the XOR of two strings';
  var slot12 = '    xor = [ord(a) ^ ord(b) for a,b in zip(key,target)]';
  var slot13 = '';
  var slot14 = '    for byte in xor:';
  var slot15 = '        #if bytes are the same we have a collision; keep going'
  var slot16 = '        if byte == 0:';
  var slot17 = '             count += 1';
  var slot18 = '        else:';
  var slot19 = '             return count';
  var slot20 = '';
  var slot21 = '';
  var slot22 = 'def main():';
  var slot23 = '        while True:';
  var slot24 = '            if find_collision():';
  var slot25 = '                shadowCaster.releaseLight()';
  var slot26 = '            else:';
  var slot27 = '                shadowCaster.acquireLight()';
}


function setup() {
  createCanvas(canvasWidth, canvasHeight);
  frameRate(20); //sets rate of draw to 20 calls per second instead of 60
}

function draw() {
  background(0); // changes background color of page
  if (checkOrder()) {
    // winning screen
    fill(255);
    textSize(50);
    if (game == "one"){
      document.location = "/release?e=1105c5f96792b0daeea7b2c49b655e3d3fdd6d45";
    }else if (game == "two"){
      document.location = "/release?e=16443c5b905d9762076343199cd3798817ed5898";
    }
    //text("you win", 200, 200);
  } else {
    dragGame();
  }
}

var textAttr = [];
var counter = 0;
var properSlot = 0;
if (game == "one"){
  var currSlot = [0, 1, 2, 3, 6, 5, 4]; //default starting position
}else if(game == "two"){
  var currSlot = [6, 4, 3, 1, 0, 5, 2]; //default starting position  
}
for (var i = 0; i < currSlot.length; i++) {
  textAttr.push([false]);
  var megaStr = '';
  if(game=="one"){
    for (var j = 0; j < 1; j++) {
      megaStr = megaStr + eval("slot" + counter.toString()) + "\r\n"; //allows for dynamic implementation? may remove later, eval con be harmful
      counter++;
    }
  }else if(game == "two"){
    for (var j = 0; j < 4; j++) {
      megaStr = megaStr + eval("slot" + counter.toString()) + "\r\n"; //allows for dynamic implementation? may remove later, eval con be harmful
      counter++;
    }    
  }

  textAttr[i].push(megaStr);
  textAttr[i].push(properSlot);
  properSlot++;
  textAttr[i].push(currSlot[i]);
}
// in textAttr, 0 is isMoving, 1 is string, 2 is proper place, 3 is current space

function dragGame() {
  if(game == "one"){
    textSize(height / 42);
  }else if(game == "two"){
    textSize(height / 42);
  }
  textFont('Quantico');
  for (var i = 0; i < textAttr.length; i++) {
    if (textAttr[i][0] === false) {
      fill(60, 60, 100); //color of boxes
      rect(width / 8, height * textAttr[i][3] * 4 / 28, width * 3 / 4, height * 4 / 28);
      // height of rect is (height * numberOfLineInBox / TotalNumberOfLines)
      fill(255); //color of text
      if(game == "one"){
        text(textAttr[i][1], width / 8 + height / 28, height * textAttr[i][3] * 4 / 28 + height / 15);
      }else if(game == "two"){
        text(textAttr[i][1], width / 8 + height / 28, height * textAttr[i][3] * 4 / 28 + height / 28);
      }
      
      // (height / 28) is the offset for readability
    } else {
      fill(60, 60, 100); //color of boxes
      rect(mouseX, mouseY, width * 3 / 4, height * 4 / 28);
      fill(255); //color of text
      text(textAttr[i][1], mouseX + height / 28, mouseY + height / 28);
    }
  }
}

function checkOrder() {
  for (var i = 0; i < textAttr.length; i++) {
    if (textAttr[i][3] != textAttr[i][2]) {
      return false;
    }
  }
  return true;
}

function touchStarted() {
  console.log(textAttr);
  if (mouseX > width / 8 && mouseX < width * 7 / 8) {
    var tempMoving = Math.abs(Math.floor(mouseY * textAttr.length / height));
    if (tempMoving > textAttr.length - 1) { //fix release off screen
      tempMoving = textAttr.length - 1;
    } else if (tempMoving < 0) {
      tempMoving = 0;
    }
    for (var i = 0; i < textAttr.length; i++) {
      if (textAttr[i][3] == tempMoving) {
        textAttr[i][0] = true;
      }
    }
    for (var i = 0; i < textAttr.length; i++) {
      if (textAttr[i][0] === true) {
        for (var j = 0; j < textAttr.length; j++) {
          if (textAttr[i][3] < textAttr[j][3] && textAttr[j][0] === false) {
            if (textAttr[j][3] - 1 >= 0) {
              textAttr[j][3] -= 1;
            }
          }
        }
      }
    }
  }
  return false; //prevent default browser behavior
}

function touchEnded() {
  for (var i = 0; i < textAttr.length; i++) {
    if (textAttr[i][0]) {
      textAttr[i][0] = false;
      var tempEnd = Math.floor(mouseY * textAttr.length / height);
      if (tempEnd > textAttr.length - 1) {
        textAttr[i][3] = textAttr.length - 1;
      } else if (tempEnd < 0) {
        textAttr[i][3] = 0;
      } else {
        textAttr[i][3] = tempEnd;
      }
      for (var j = 0; j < textAttr.length; j++) {
        if (textAttr[j][3] >= textAttr[i][3] && i != j && textAttr[j][0] === false) {
          textAttr[j][3] += 1;
        }
      }
    }
  }
  return false; //prevent default browser behavior
}

function countLines(str) { //possibly use to generate dynamically, currently unused
  return str.split(/\r\n|\r|\n/).length;
}