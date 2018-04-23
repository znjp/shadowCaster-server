var goal = Math.round(Math.random() * 204) + 51;
switches = [];
for (var i = 0; i < 8; i++) {
  switches.push(false);
}
if (game == "int") {
  document.getElementById('mainHeading').innerHTML = goal;
} else if (game == "hex") {
  document.getElementById('mainHeading').innerHTML = "0x" + goal.toString(16);
}

function toggle(binNum) {
  var btn = $('#' + binNum)
  btn.toggleClass('on')
  btn.toggleClass('off')
  switches[binNum] = !switches[binNum]
  if ($('#bin' + binNum).html() == '0') {
    $('#bin' + binNum).html('1')
  } else {
    $('#bin' + binNum).html('0')
  }
  currentNum = boolArrayToDec(switches)
  if (currentNum == goal) {
    if (game == "int") {
      document.location = "/release?e=3b10e318779364e186c2fe7b7f8e07e40bf9eaf5"
    } else if (game == "hex") {
      document.location = "/release?e=587db024ee9e68fbeee8c799a2ce0c142ae67597"
    }
  }
}

function boolArrayToDec(array) {

  total = 0
  for (var i = 0; i < array.length; i++) {
    if (array[array.length - 1 - i]) {
      total += Math.pow(2, i);
    }
  }
  return total
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