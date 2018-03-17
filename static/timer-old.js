/* Iterates the timer, to be called each second by a setInterval(..., 1000); */
function iterTimer(element) {
    var timer = localStorage.stun_timer;
    if (timer !== undefined) {
        var minutes = parseInt(timer / 60, 10);
        var seconds = parseInt(timer % 60, 10);

        var minStr = minutes < 10 ? "0" + minutes : minutes;
        var secStr = seconds < 10 ? "0" + seconds : seconds;

        element.innerText = minStr + ":" + secStr;
        if (--timer <= 0) {
            /* wipe the interval callback and the timer info */
            clearInterval(localStorage.stun_timer_id);
            delete localStorage.stun_timer_id
            delete localStorage.stun_timer;
        }
        else {
            /* Tick forward the clock to persist over reloads */
            localStorage.stun_timer = timer;
        }
    }
}

/* takes an HTML Element
 * Start (or restart, after page reload) a timer
 */
function startTimer(element) {
    localStorage.setItem("stun_timer_id", setInterval(iterTimer, 1000, element));
}

/* Must be called for startTimer to do anything
 * Give an HTML Element and a duration
 */
function setTimer(element, duration) {
    delete localStorage.stun_timer_id
    delete localStorage.stun_timer;
    localStorage.setItem("stun_timer", duration);
    startTimer(element); /* set a 5-minute timer on elem */
    return true;
}

/* Main, if you will. Checks for localStorage and runs a new
 * timer, or continues an existing one.
 
if (typeof(Storage) !== undefined) {
    var elem = document.getElementById("stun-timer");
    if (localStorage.stun_timer === undefined) {
        setTimer(elem, 15);
    }
    else {
        startTimer(elem);
    }

}
*/