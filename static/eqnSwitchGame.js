var goal1 = Math.round(Math.random() * 204) + 51;
var goal2 = Math.round(Math.random() * 204) + 51;
var goal3 = Math.round(Math.random() * 204) + 51;

document.getElementById('mainHeading').innerHTML = goal1 + " ^ 0" + goal2.toString(8) + ' | ~0x' + goal3.toString(16) + ' & 0b11111111';

var goal = Math.round(Math.random() * 204) + 51;
$('#mainHeading').innerHTML = 'Please Convert ' + goal + ' from Decimal to Binary';

switches = [];
for (var i = 0; i < 8; i++) {
  switches.push(false);
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

function toggle(binNum) {
  var btn = $('#' + binNum)
  btn.toggleClass('on')
  btn.toggleClass('off')
  switches[binNum] = !switches[binNum]
  if ($('#bin' + binNum + '.counter').html() == '0') {
    $('#bin' + binNum + '.counter').html('1')
  } else {
    $('#bin' + binNum + '.counter').html('0')
  }
  // document.getElementById('currentNum').innerHTML = boolArrayToDec(switches)
  // if (currentNum == goal1 ^ goal2 | ~goal3 & 255) {
  //   document.location = "/release?e=14265e37fd16904ee3d4a306ff25016de9181eb8";
  // }
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


// hasClass, addClass, removeClass are from https://jaketrent.com/post/addremove-classes-raw-javascript/

function hasClass(el, className) {
  if (el.classList)
    return el.classList.contains(className)
  else
    return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'))
}

function addClass(el, className) {
  if (el.classList)
    el.classList.add(className)
  else if (!hasClass(el, className)) el.className += " " + className
}

function removeClass(el, className) {
  if (el.classList)
    el.classList.remove(className)
  else if (hasClass(el, className)) {
    var reg = new RegExp('(\\s|^)' + className + '(\\s|$)')
    el.className = el.className.replace(reg, ' ')
  }
}