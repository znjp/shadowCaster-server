

# TODO

## High Priority
- Refactor JS code to have a shadowcaster library

- <strike>Simon: touch feedback</strike>

- <strike>Toggles: make work for all mobile</strike>

- <strike>Switches: Make them circles</strike>

- <strike>fix 9</strike>

- <strike>when changing shadowcaster # reset the database, including recomputing flags</strike>

- SC13: Make wheel drag with a touch/tap

- <strike>NB: Create a separete "releasing light" state, which looks visually distinct from stunning, as conflating with stunning is confusing</strike>

- <strike>NB: Color needs to be correctly set on boot/reboot</strike>

- NB: Determine best way to integrate UnicornHat project

- Flags/passwords must not have ambigious characters; look into English word maps or Base58 encoding

- Double check to see if the XML Request code for checking stun status is correct; meaning that connections are properly closed. (Some of our previous failing issues came from having too many open connections.)

- NB: Fix tabbing issue that shows the puzzle underneath stunning timer on "sc" page

### Low to Medium Priority
- <strike>Shorter flags, in case copy and paste doesn't work</strike>

- <strike>Reveal flag on "you've already released this flag" page </strike>

- NB: Create a way for flags to be auto-submitted should a WiFi network exist. So the puzzle it only served on a private network, but flags can be submitted to a public scorebaord.

- Create a flag generation scheme that can't be solved through code inspection; will require server-side verification; H(r || solved state?); this might need to be per-puzzle, which will be a little lame

- Refactor to remove JavaScript processing; Move stun and release animations from JS to gif

- <strike>I solved SC5, then visited SC6 and it said it had already been solved. Look into this.</strike>

- Look into a hash function whose domain is english words (or write our own)

- Make puzzles simpler to integrate, or at least write some documentation on how to.

- Update stunstatus polliung to include a "Agent nearby poll"?

- NB: Add an "completely released" LED visual/state, should all the energy be drained

- More space between [] and flags/passwords and perhaps differnet color

- Better shadowCaster build: brighter LEDs; 3D printed cubes; on/off buttons; sounds?

- Move from web.py to Flask or something else? Unclear how robust web.py is to multiple connections.

- NB: Configure routers/Pi to host a DNS server; allowing puzzles to be found by http://shadowcaster 


## New Puzzle Ideas
- <strike>Lights Out</strike>
- "plug board" substitution cipher
- Morse code-type challenge; cube pulses?

#### To Categorize
##### Admin Interface for SC
 - <strike> Create a web interface for changing the shadowcaster puzzle number</strike>
 - <strike> Adjust the energy levels</strike>
 - <strike> Stun and flag duration</strike>
 - <strike> test LEDs; Get GPIO status</strike>
 - Add/remove teams; change password
 - <strike> template for printing out team credentials </strike>
 - Single button to Reset everything (all solves, energy levels) for new game
 - <strike> changing sc number resets all flags and sloved status </strike>
 - <strike>Print teams & flags<strike>

##### Real DB integration
 - <stirke> teams</strike>
 - <strike>sc settings</strike>
 - session cookies

##### Scoreboard integration
 - Have a way to configure the auto submitting of flags if the SC's can have internet access
 - Have a way to lock a team to a single shadowcaster at a time; once logged in to one, can't log into another?

##### "Push" notifications
 - Alert on puzzles screen when a ShadowAgent is near

**Running the Game**
- Rotate SA locations (inside/outside) if it's cold
- Make sure there are places to hide around SC locations
- Stunning maybe takes points away?
- Glow sticks/LED string lights for SAs
- Explain the rules of flag submitting
- More points for early solves (motivate splitting up/working independently)
- Should releasing light stun/disable the shadowCaster? If yes, it causes a mechanic where two teams at the same caster race to complete it.
- Make the last challenge helping everyone else solve the remaining challenges
- Put WiFi adapters back on Pi 2s; will allow for easier updates
- Consider adding "coallition" forces or a headquarters to contact to help with puzzles
- Have players practice connecting and flag submitting at start of game (start game at first caster?)
- "This is part of game/phone number" labels 
- More points for early solves?
