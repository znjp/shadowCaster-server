timer_duration = 0;

/* Iterates the timer, to be called each second by a setInterval(..., 1000); */
function iterTimer(element) {
    var timer = timer_duration;
    if (timer !== undefined) {
        var minutes = parseInt(timer / 60, 10);
        var seconds = parseInt(timer % 60, 10);

        var minStr = minutes < 10 ? "0" + minutes : minutes;
        var secStr = seconds < 10 ? "0" + seconds : seconds;

        element.innerText = minStr + ":" + secStr;
        if (--timer <= 0) {
            /* wipe the interval */
            timer_duration = 0;
        }
        else {
            /* Tick the clock  */
            timer_duration = timer;
        }
    }
}


/* Must be called for startTimer to do anything
 * Give an HTML Element and a duration
 */
function setTimer(element, duration) {

    timer_duration = duration;
    setInterval(iterTimer, 1000, element);

    return true;
}