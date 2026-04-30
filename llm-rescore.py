#!/usr/bin/env python3
"""
Re-score all 290 Taskmaster tasks for party suitability using human judgment
instead of keyword matching. Each task gets:
  - safety (1-5): Can this be done safely at a house party?
  - equipment (1-5): How easy to get the stuff?
  - group_fun (1-5): How fun for a party group?
  - party_notes: Specific creative note on adaptation
  - party_score = safety * equipment * group_fun
  - party_adaptable = party_score >= 48
"""

import json

# Since there are duplicate IDs, we key by index position
# Format: (safety, equipment, group_fun, party_notes)
# Index matches the order in the JSON array

SCORES = [
    # ===== S04 =====
    # 0: s04-e01-t01 | prize | Bring in the most interesting autograph on the most interesting vegetable
    (5, 5, 4, "Everyone raids the kitchen for a vegetable, then forges the funniest celebrity autograph on it. Vote on best combo."),
    # 1: s04-e01-t02 | solo | Destroy this cake beautifully. 30 min
    (4, 3, 5, "Buy cheap cupcakes. Everyone gets one and 5 minutes to destroy it beautifully using household items. Photograph results, vote on winner."),
    # 2: s04-e01-t03 | solo | Draw a person without looking at them
    (5, 5, 5, "Pick one person as the model. Everyone draws them without looking directly — use peripheral vision only. Reveal simultaneously for maximum laughs."),
    # 3: s04-e01-t04 | solo | Fell all rubber ducks. Fastest wins
    (4, 3, 4, "Line up plastic cups on a table. Everyone stands behind a line and throws socks/balls to knock them down. Fastest wins."),
    # 4: s04-e02-t01 | prize | Bring in your most boastful item
    (5, 5, 5, "Everyone finds the most brag-worthy thing in their phone or wallet. Present it to the group with maximum swagger. Vote on best humble-brag."),
    # 5: s04-e02-t02 | solo | Keep basketball on running machine
    (2, 1, 2, "Doesn't work at a party — requires a treadmill, a basketball, and way too much time. Skip this one."),
    # 6: s04-e02-t03 | solo | Paint Taskmaster from behind a line
    (4, 4, 5, "Tape a line on the floor 2 metres from the paper. Everyone paints a portrait of the host from behind the line using long-handled brushes or thrown paint."),
    # 7: s04-e02-t04 | team | Plant flour on target from bandstand
    (3, 3, 4, "Too messy for indoors. Could work in a garden — teams throw flour balls at a target from behind a rope. Loser cleans up."),
    # 8: s04-e02-t05 | solo | Move egg between cups without touching
    (5, 5, 4, "Set up two egg cups at opposite ends of a table. Everyone gets a go at moving the egg without touching egg or cup. Spoon, straw, breath — creativity wins."),
    # 9: s04-e02-t06 | live | Attach balloons under a smock while maintaining eye contact
    (5, 4, 5, "Everyone wears a big shirt/jacket. Hands underneath, maintain eye contact with the host. Tie balloons together for 100 seconds. Longest chain wins."),
    # 10: s04-e03-t01 | prize | Bring in the best membership/subscription
    (5, 5, 4, "Everyone pulls up the weirdest subscription or membership they actually have on their phone. Present and vote. Bonus for forgotten recurring charges."),
    # 11: s04-e03-t02 | solo | Camouflage yourself. 20 min total
    (5, 4, 5, "Everyone gets 5 minutes to hide somewhere in the house using only what's available. The host counts to 60 then photographs every room. Best camouflage wins."),
    # 12: s04-e03-t03 | team | Make a movie trailer for Taskmaster
    (5, 5, 5, "Teams of 3 get 10 minutes to film a 30-second movie trailer on their phones. Screen them for the group. Audience votes best trailer."),
    # 13: s04-e03-t04 | solo | Persuade dogs/chickens to stand on mat
    (3, 2, 3, "Requires live animals. Could adapt with a house cat if one is available — lure the cat onto a cushion. Otherwise skip."),
    # 14: s04-e03-t05 | solo | Transfer water from fishbowl A to B using only table items
    (4, 3, 4, "Set up two bowls of water 2 metres apart. Provide random kitchen items (baguette, sponge, tube). Transfer water without moving the bowls. Messiest solution gets bonus points."),
    # 15: s04-e03-t06 | live | Say N-letter word when music stops
    (5, 5, 5, "Play music on a phone, pause randomly. The required word length changes each round (5, then 6, then 3...). Hesitate or repeat a word = eliminated."),
    # 16: s04-e04-t01 | prize | Bring in your most surprising picture of yourself
    (5, 5, 5, "Everyone scrolls through their camera roll and finds the most surprising/embarrassing photo of themselves. Show on TV or pass phone around. Group votes."),
    # 17: s04-e04-t02 | solo | Make the highest splash. 15 min
    (2, 2, 3, "Requires outdoor water source and 15 minutes of setup. Not practical for a house party unless you have a garden with a paddling pool."),
    # 18: s04-e04-t03 | solo | Choreograph a dance with Alex to a ringtone
    (5, 5, 5, "Pairs choreograph a 30-second dance to a random phone ringtone. 5 minutes to rehearse, then perform for the group. Audience scores."),
    # 19: s04-e04-t04 | solo | Draw a well-known person using only toilet roll
    (5, 5, 5, "Everyone gets a toilet roll and 3 minutes. Tear/shape/draw on it to create a recognizable celebrity. Reveal simultaneously. Group guesses who each one is."),
    # 20: s04-e04-t05 | solo | Do the most incredible thing with this pommel horse
    (3, 1, 3, "Requires a pommel horse or similarly large prop. Not practical for a house party."),
    # 21: s04-e04-t06 | live | Make highest tower using cardboard tubes. 100 sec
    (5, 4, 5, "Give everyone toilet roll tubes or cardboard tubes. 100 seconds to build the tallest freestanding tower. Dramatic collapses guaranteed."),
    # 22: s04-e05-t01 | prize | Bring in your cutest thing
    (5, 5, 4, "Everyone finds the cutest thing in the room or on their phone. Baby photos, pet pics, tiny objects. Present with maximum 'aww' energy. Group votes."),
    # 23: s04-e05-t02 | solo | Slide the furthest. 20 min
    (2, 2, 3, "Requires outdoor space and lubricant. Too dangerous and messy for a house party. Fun to watch the clip though."),
    # 24: s04-e05-t03 | solo | Put on wetsuit while video-calling a Swedish person
    (5, 2, 4, "Needs a wetsuit and a willing stranger on video call. Could adapt: FaceTime a random contact while putting on as many layers of clothing as possible."),
    # 25: s04-e05-t04 | team | Whispered tin can telephone tasks
    (5, 3, 5, "Pairs use tin cans and string (or just cupped hands). Whisper a silly instruction. Partner must decode and execute it. Hilarious miscommunication guaranteed."),
    # 26: s04-e05-t05 | solo | Throw something into something. Most unbelievable throw
    (4, 5, 5, "Everyone gets 3 attempts to make the most impressive trick throw — coin into a cup, ball into a bin across the room. Film each attempt. Best highlight reel wins."),
    # 27: s04-e05-t06 | live | Make longest continuous noise
    (5, 5, 5, "Everyone wears headphones playing loud music. Make the longest continuous noise without hearing yourself. Time each person. Bonus point for best noise."),
    # 28: s04-e06-t01 | prize | Bring in your best sheep-related item
    (5, 5, 4, "Everyone finds or creates the best item related to a randomly assigned animal. Woolly socks, toy sheep, lamb photos — present and vote."),
    # 29: s04-e06-t02 | solo | Get camel through smallest gap
    (5, 4, 4, "Use a stuffed toy or action figure. Everyone tries to fit it through the smallest gap they can find in the house. Measure the gap — smallest wins."),
    # 30: s04-e06-t03 | solo | Score goal with plastic bag
    (4, 5, 4, "Set up a goal with cushions. Everyone kicks a plastic bag from across the room. Fewest kicks and most stylish finish wins. Hugh's overhead kick energy."),
    # 31: s04-e06-t04 | solo | Identify items in sleeping bag by touch
    (5, 4, 5, "Fill a pillowcase with 5 mystery items from around the house. Everyone takes turns reaching in blindfolded. Most correct guesses wins. Hilarious wrong answers."),
    # 32: s04-e06-t05 | live | Prepare items then do surprise task with them
    (5, 4, 5, "Give everyone 5 random items to 'prepare however they want.' Then reveal the real task: hold all items in one hand while doing something difficult. Chaos ensues."),
    # 33: s04-e07-t01 | prize | Bring in your best chair
    (5, 5, 4, "Everyone picks the best chair in the house and presents their case for why it's the greatest chair. Dramatic chair reviews. Group votes."),
    # 34: s04-e07-t02 | solo | Stand on one leg, deliver sandwich to Alex
    (5, 5, 5, "Everyone hops on one leg to deliver a drink across the room. Touch the floor = take a sip of your drink. First to deliver with the most remaining wins."),
    # 35: s04-e07-t03 | solo | Hide from Alex. Hide and seek
    (5, 5, 5, "Classic hide and seek in the house. One seeker, everyone hides. 5-minute time limit. Last found wins. Great icebreaker for house parties."),
    # 36: s04-e07-t04 | team | Wheelie bin race, one blindfolded, foreign language directions
    (3, 2, 4, "Needs a wheelie bin and outdoor space. Adapt indoors: blindfold one partner, they navigate the room via directions in a fake language. Reach the target object."),
    # 37: s04-e07-t05 | solo | Create best and most original handshake
    (5, 5, 5, "Pairs invent the most elaborate handshake in 3 minutes. Perform for the group. Audience scores on creativity, commitment, and awkwardness."),
    # 38: s04-e07-t06 | live | Make the best big banana from bananas. 100 sec
    (5, 4, 5, "Give everyone a banana and tape/glue. 100 seconds to make the biggest or most impressive banana sculpture. Peel, mash, stack — anything goes."),
    # 39: s04-e08-t01 | prize | Bring in the most cash
    (5, 5, 5, "Everyone empties their pockets/wallets. Most creative interpretation of 'most cash' wins — foreign coins, Monopoly money, Venmo screenshots all count."),
    # 40: s04-e08-t02 | solo | Make most exotic sandwich then eat it
    (5, 4, 5, "Raid the kitchen. Everyone makes the most exotic sandwich in 5 minutes using whatever they find. Then you MUST eat it. Group votes on ambition vs. regret."),
    # 41: s04-e08-t03 | solo | Hit cheese as far as possible with snooker cue
    (3, 2, 3, "Needs a snooker cue and outdoor space. Could adapt: flick a cheese cube off a table with a ruler. Furthest landing wins. Measure with a tape."),
    # 42: s04-e08-t04 | solo | Do something surprising with a rubber duck
    (5, 4, 5, "Give everyone a random household object (not a duck, but similar). 5 minutes to prepare the most surprising reveal. Present one by one. Genuine surprises win."),
    # 43: s04-e08-t05 | live | Draw the median duck
    (5, 5, 5, "Everyone draws a duck. But the goal is to draw the MIDDLE-sized one — not biggest, not smallest. Median duck wins. Brilliant because trying to be average is surprisingly hard."),

    # ===== S05 =====
    # 44: s05-e01-t01 | prize | Bring in something that makes the most excellent noise
    (5, 5, 4, "Everyone finds something in the house that makes a great noise. Present your noise. Group votes on most satisfying sound."),
    # 45: s05-e01-t02 | special | Give Alex a special cuddle
    (4, 5, 5, "Everyone gives the host the most creative, theatrical hug they can think of. One at a time, 30 seconds each. Group votes on most special cuddle."),
    # 46: s05-e01-t03 | solo | Get Alex from boat to dry land elegantly
    (2, 1, 3, "Requires a pond and a boat. Not doable at a house party."),
    # 47: s05-e01-t04 | solo | Basketball through hoop without hands
    (4, 2, 4, "Need a hoop and basketball. Could use a bin and a ball — get the ball in the bin without using hands. Feet, head, elbows only. Everyone gets 3 attempts."),
    # 48: s05-e01-t05 | live | Get fruit into fishbowl without leaving chair or throwing
    (5, 4, 5, "Everyone sits around a table with a bowl of fruit and an empty bowl in the center. Get your fruit into the center bowl without standing, throwing, or touching with hands."),
    # 49: s05-e02-t01 | prize | Bring in hippest headwear
    (5, 5, 4, "Everyone fashions headwear from whatever they can find in 2 minutes — towels, bowls, tinfoil. Runway walk to show it off. Group votes hippest."),
    # 50: s05-e02-t02 | solo | Make best coconut flinging machine
    (3, 2, 3, "Needs outdoor space and building materials. Not practical for a house party unless you have a garden and don't mind chaos."),
    # 51: s05-e02-t03 | solo | Paint best rainbow scene in complete darkness
    (5, 4, 5, "Turn off all lights. Give everyone paper and markers. 3 minutes to draw a rainbow scene in total darkness. Turn lights on — reveal the chaos. Best attempt wins."),
    # 52: s05-e02-t04 | solo | Slice bread with one non-knife tool
    (4, 4, 4, "Give everyone a slice of bread and a random non-knife tool (credit card, ruler, string). Neatest slice wins. Messy and funny."),
    # 53: s05-e02-t05 | team | Greatest splat using a crane
    (1, 1, 3, "Requires a crane and outdoor space. Completely impractical for any house party. Skip."),
    # 54: s05-e02-t06 | live | Paint through a face hole in a board
    (5, 3, 5, "Cut a face hole in cardboard. Everyone paints an animal around their own face in 3 minutes. The face-as-part-of-the-painting results are always hilarious."),
    # 55: s05-e03-t01 | prize | Bring in the thing you're actually proudest of
    (5, 5, 5, "Everyone shares the thing they're genuinely most proud of — photo on phone, a skill, a story. Surprisingly wholesome and great for bonding. Group votes."),
    # 56: s05-e03-t02 | solo | Get table tennis ball out of pipe
    (5, 4, 5, "Put a ping pong ball in a tall glass or bottle. Get it out without tipping the container. Classic puzzle — pour water in to float it up. Race to solve it."),
    # 57: s05-e03-t03 | solo | Make coconut look like a businessman
    (5, 4, 5, "Give everyone a potato or apple and office supplies (pen, paper, tape). 5 minutes to make it look like a businessman. Board meeting of potato executives."),
    # 58: s05-e03-t04 | solo | Three items, three tasks — eat/throw/balance
    (5, 4, 5, "Set three items on the table (cracker, grape, spoon). You must eat one, throw one in a bucket, balance one on your head. Each item used only once. Fastest wins."),
    # 59: s05-e03-t05 | live | Word chain table tennis
    (5, 5, 5, "Stand across a table. Mime hitting a ping pong ball while saying a word starting with the last letter of the previous word. Hesitate = out. Fast and furious."),
    # 60: s05-e04-t01 | prize | Bring in your most extraordinary souvenir
    (5, 5, 4, "Everyone finds the most interesting object they have on them or in their bag. Present the story behind it. Most extraordinary backstory wins."),
    # 61: s05-e04-t02 | solo | Make Marmite from available ingredients
    (5, 4, 4, "Everyone raids the kitchen to create a mystery condiment in 5 minutes. Others must taste and guess what they were going for. Closest to target flavour wins."),
    # 62: s05-e04-t03 | team | Do something remarkably synchronized
    (5, 5, 5, "Teams of 2-3 get 5 minutes to rehearse the most synchronized routine they can — a dance, simultaneous actions, mirror movements. Perform for the group."),
    # 63: s05-e04-t04 | solo | Blow up balloon to cucumber size, then spot 10 room changes
    (5, 5, 5, "Blindfold everyone. While blindfolded, blow up a balloon to a specific size. Then remove blindfold — 10 things in the room have changed. Spot them all. Two great games in one."),
    # 64: s05-e04-t05 | solo | Sneeze. Fastest wins
    (5, 5, 5, "Everyone must produce a genuine sneeze as fast as possible. Timer starts on 'go.' Pepper allowed. Fake sneezes disqualified. Simple, absurd, hilarious."),
    # 65: s05-e04-t06 | live | One leg + Simon Says + balloon under foot
    (4, 4, 5, "Stand on one leg holding a balloon under your raised foot. Play Simon Says. Drop your foot = balloon pops = you're out. Intense and funny."),
    # 66: s05-e05-t01 | prize | Bring in your most high-octane item
    (5, 5, 4, "Everyone nominates the most exciting/adrenaline-inducing thing they can show on their phone or find in the house. Energy drink cans count. Vote."),
    # 67: s05-e05-t02 | solo | Put biggest thing in balloon, inflate, tie
    (5, 4, 4, "Give everyone a balloon. Stuff the biggest item you can fit inside, then inflate and tie the balloon. Biggest successful balloon wins."),
    # 68: s05-e05-t03 | solo | Create most remarkable water cooler moment. 1 hour
    (5, 5, 4, "Shorten to 5 minutes. Create the most remarkable moment in the room right now using only what's available. Perform for the group. Vote on most water-cooler-worthy."),
    # 69: s05-e05-t04 | special | Send anonymous cheeky texts for 5 months
    (5, 5, 2, "Long-term secret task. Doesn't work in a single-evening party format. Could adapt: everyone sends one anonymous cheeky text to the host during the party."),
    # 70: s05-e05-t05 | solo | Tallest can tower while shaking hands and naming countries
    (5, 4, 5, "Stack cans/cups into the tallest tower. Every 10 seconds, shake someone's hand and claim to be from a different country. Miss a handshake = tower resets."),
    # 71: s05-e05-t06 | live | Find the Finns by asking one question each
    (5, 5, 5, "Line up 5 people. One is secretly 'the Finn.' Each player asks one person one question (not about nationality). Deduce who the Finn is. Works great with party guests playing along."),
    # 72: s05-e06-t01 | prize | Bring in best thing you've made yourself
    (5, 5, 4, "Everyone shows the best thing they've ever made — craft, meal photo, code, art. Pull it up on phones. Present to the group. Most impressive wins."),
    # 73: s05-e06-t02 | solo | Balance Alex on seesaw with counterweights
    (3, 2, 3, "Requires a seesaw. Not practical for a house party. Could vaguely adapt with a balance scale and guessing someone's weight in household items."),
    # 74: s05-e06-t03 | solo | Record incredible head-cam footage
    (4, 4, 3, "Strap a phone to your head and film the most incredible footage in the house in 3 minutes. Watch back on TV. Surprisingly nauseating and funny."),
    # 75: s05-e06-t04 | solo | (empty task)
    (5, 5, 3, "No task description available. Cannot score meaningfully."),
    # 76: s05-e06-t05 | special | Golden pineapple photo portfolio over 6 months
    (5, 5, 2, "Long-term task — doesn't work at a party. Would need weeks of lead time."),
    # 77: s05-e06-t06 | solo | Light candle in caravan using a flame, can't say words with letter
    (3, 3, 4, "Transport a lit candle across the room while avoiding saying any words containing the letter 'S.' Everyone does it simultaneously. First to arrive without a speech violation wins."),
    # 78: s05-e06-t07 | live | Make yourself monotone in 100 seconds
    (4, 4, 5, "Everyone gets 100 seconds, a bin bag, and tape. Make yourself completely one colour from the shoulders down. Most monotone wins. Quick and silly."),
    # 79: s05-e07-t01 | prize | Bring in most surprisingly expensive item
    (5, 5, 5, "Everyone shows something that looks cheap but is actually expensive (or vice versa). Group guesses the price first. Best surprise gap wins."),
    # 80: s05-e07-t02 | solo | Walk blindfolded for 3 min, retrace steps
    (5, 5, 4, "Blindfolded, walk around the room for 1 minute. Remove blindfold and try to retrace your exact path backwards. Film both and compare. Closest retrace wins."),
    # 81: s05-e07-t03 | team | Coconut bobsled team
    (3, 2, 3, "Needs a slope and a sled. Not practical indoors. Could adapt: load a serving tray with oranges and slide it across a table. Most fruit still on the tray wins."),
    # 82: s05-e07-t04 | live | Send items via zipline to Taskmaster's table
    (4, 2, 4, "Needs a zipline setup. Could rig a simple string line across the room. Send items down to land on a target plate. But setup is fiddly."),
    # 83: s05-e08-t01 | prize | Bring in most awkward item for someone else to take home
    (5, 5, 5, "Everyone wraps up the most awkward item from the house. White elephant exchange. The recipient must carry it home. Cringe factor is the scoring metric."),
    # 84: s05-e08-t02 | solo | Get coconut far without touching ground
    (4, 3, 3, "Floor is lava with a coconut. Possible but needs cushions/furniture stepping stones. Could adapt with a ball and scattered magazines across the floor."),
    # 85: s05-e08-t03 | solo | Create the best graph. 20 min
    (5, 5, 5, "Everyone draws the funniest graph in 3 minutes — 'My confidence vs. drinks consumed,' 'likelihood of texting ex vs. time of night.' Present to the group."),
    # 86: s05-e08-t04 | solo | Most fish puns in one minute
    (5, 5, 5, "One minute on the clock. Most puns on a chosen category wins. Do multiple rounds with different topics — fish, fruit, countries. Rapid-fire hilarity."),
    # 87: s05-e08-t05 | live | Throw egg through hoop and catch it
    (3, 3, 4, "Risky indoors. Use a soft ball and a hoop made from a coat hanger. Throw through and catch on the other side. Most successful catches in 60 seconds wins."),

    # ===== S07 =====
    # 88: s07-e01-t01 | prize | Bring in thing most people would like to touch
    (5, 5, 5, "Everyone finds the most touchable thing in the room — velvet cushion, fluffy blanket, cold glass. Pass them around. Group votes on most satisfying texture."),
    # 89: s07-e01-t02 | solo | Design and demonstrate best quick change outfit
    (5, 4, 5, "Everyone gets 10 minutes to rig a quick-change outfit from available clothing. Then demonstrate the fastest transformation. Time each reveal."),
    # 90: s07-e01-t03 | solo | Build tallest tower from flat-pack boxes
    (5, 3, 4, "No flat-pack boxes at a party. Use cereal boxes, shoe boxes, whatever cardboard is around. 5-minute tower build. Tallest freestanding wins."),
    # 91: s07-e01-t04 | solo | Work out circumference of caravan in baked beans
    (5, 5, 5, "Estimate something absurd — how many grapes would fit around the sofa? How many coins across the kitchen table? Closest guess wins. No measuring allowed."),
    # 92: s07-e01-t05 | live | Make best fruit display hat using grabber tools only
    (5, 3, 5, "Everyone wears a hat. Using only kitchen tongs, arrange fruit on your hat. Cannot touch fruit or hat with hands. 100 seconds. Most elaborate fruit hat wins."),
    # 93: s07-e02-t01 | prize | Bring in the boldest belt
    (5, 5, 4, "Everyone fashions the boldest belt from household items — extension cord, tinfoil, a scarf. Runway walk. Most outrageous belt wins."),
    # 94: s07-e02-t02 | solo | Write 10-word story while running
    (4, 5, 5, "Sprint across the room while writing a 10-word story. Must be legible and coherent. Fastest with a valid story wins."),
    # 95: s07-e02-t03 | team | Blindfolded painting directed by partner
    (5, 4, 5, "Teams of 2. One blindfolded with a marker, the other directs using only 5 approved words (up, down, left, right, stop). Draw a specific object. Most recognizable wins."),
    # 96: s07-e02-t04 | solo | Draw biggest and best circle in one sweep
    (5, 5, 5, "Everyone draws a single circle in one motion on paper. Judged on both size and roundness. Use a plate as a reference for judging. Surprisingly competitive."),
    # 97: s07-e03-t01 | prize | Bring in best thing from the 90s
    (5, 5, 5, "Everyone picks the best 90s thing they can find — a song on Spotify, a photo, an item of clothing. Present with full nostalgia energy. Group votes."),
    # 98: s07-e03-t02 | solo | Greatest increase in Alex's heart rate
    (4, 5, 5, "Pick one person as the target. Everyone gets 2 minutes to raise their heart rate as much as possible — jump scares, sprints, awkward confessions. Measure with a phone app."),
    # 99: s07-e03-t03 | solo | Make the best noise
    (5, 5, 5, "Everyone prepares one incredible noise using anything in the room. Say 'this is my best noise,' make it, then freeze. Group votes on best single noise."),
    # 100: s07-e04-t01 | prize | Bring in the most confusing thing
    (5, 5, 5, "Everyone finds the most confusing thing in the house or on their phone. Present it. If the group can't figure out what it is or why it exists, you win."),
    # 101: s07-e04-t02 | solo | What happens when you flick this switch
    (5, 5, 4, "Hide a device in the house connected to a switch (a phone playing music, a lamp). Everyone investigates. First to correctly identify what the switch controls wins."),
    # 102: s07-e04-t03 | solo | Dramatically alter appearance in 18 seconds
    (5, 5, 5, "Everyone gets a bag of random items (scarves, hats, glasses, markers). 18 seconds to transform your appearance as dramatically as possible. Before/after photos."),
    # 103: s07-e04-t04 | solo | Make scales read exactly 31.770 kg
    (5, 3, 3, "Needs precise scales. Could adapt: guess the weight of a specific combo of items. Closest to the target weight wins."),
    # 104: s07-e04-t05 | live | Don the most items of clothing in 100 seconds
    (5, 5, 5, "Dump a pile of clothes in the center. 100 seconds to put on as many items as possible. Only correctly worn items count — no draping. A classic party game."),
    # 105: s07-e05-t01 | prize | Bring in worst present from a named relative
    (5, 5, 5, "Everyone shares the worst gift they've ever received. Tell the story. Group votes on most disappointing. Bonus if you can show a photo."),
    # 106: s07-e05-t02 | solo | Deliver task to Alex in most spectacular way
    (5, 5, 4, "Give everyone a note that says 'Read me to [host].' Most spectacular delivery method wins — song, dance, elaborate reveal. Creativity over speed."),
    # 107: s07-e05-t03 | team | Make white circles on target from behind rope
    (5, 4, 4, "Tape a target on the wall. Everyone throws paper circles (hole-punched) from behind a line. Most circles on the target wins. Simple and competitive."),
    # 108: s07-e05-t04 | solo | Cheer up this grumpy traffic warden
    (5, 5, 5, "Nominate the grumpiest person at the party. Everyone gets 2 minutes to cheer them up. The grump scores each attempt out of 10. Highest score wins."),
    # 109: s07-e05-t05 | live | Make yourself look as little/big as possible
    (5, 5, 5, "Using forced perspective and a phone camera, make yourself look as tiny or as giant as possible. Best optical illusion photo wins."),
    # 110: s07-e06-t01 | prize | Bring in the best key
    (5, 5, 4, "Everyone empties their keyring. Present each key with a dramatic backstory — real or invented. Best key narrative wins."),
    # 111: s07-e06-t02 (first) | solo | Put exactly 50 different things in this bin
    (5, 5, 4, "Race to gather exactly 50 different items and place them in a container. Go over or under = disqualified. Speed matters but so does counting."),
    # 112: s07-e06-t02 (second) | solo | Make best picture of Taskmaster using all items on mat
    (5, 5, 5, "Using whatever 10 random items are on the table, create a portrait of someone in the room. Everyone does it simultaneously. Most recognizable face wins."),
    # 113: s07-e06-t03 | team | Write and perform most suspenseful soap opera cliffhanger
    (5, 5, 5, "Teams of 2-3 write and perform a 1-minute soap opera cliffhanger. Must include a dramatic reveal. Audience scores on gasps per minute."),
    # 114: s07-e06-t04 | solo | Put 10 pairs of glasses in smallest box
    (5, 4, 4, "Collect 10 small items (pens, coins, keys). Fit them all in the smallest container you can find with the lid closed. Smallest successful container wins."),
    # 115: s07-e06-t05 | live | Get donut as high as possible while holding hands
    (5, 4, 5, "Everyone holds hands in a line. Each person has a donut. Get your donut as high as possible in 100 seconds without breaking the chain. Teamwork meets chaos."),
    # 116: s07-e07-t01 | prize | Bring in most exciting thing beginning with G
    (5, 5, 4, "Pick a random letter. Everyone finds the most exciting thing starting with that letter in 2 minutes. Present and vote. Rotate letters for multiple rounds."),
    # 117: s07-e07-t02 | solo | Throw something into bin over tall fence
    (4, 3, 3, "Needs a tall barrier. Could throw items over the back of a sofa into a bin on the other side. Three attempts each. Most accurate thrower wins."),
    # 118: s07-e07-t03 | solo | Don't blink. Last to blink wins
    (5, 5, 5, "Classic staring contest. Pairs face off. Last to blink advances. Quick elimination rounds until a champion is crowned. No tape on eyelids allowed."),
    # 119: s07-e07-t04 | team | Make best extension to the Taskmaster house
    (5, 4, 4, "Teams build the best 'extension' to a room using cardboard, blankets, cushions. 10 minutes. Present the estate agent tour of your new room extension."),
    # 120: s07-e07-t05 | solo | Make the best Christmas cracker
    (5, 4, 4, "Everyone makes a cracker from a toilet roll tube, wrapping paper, and writes a joke + makes a tiny prize. Pull them with a partner at the end."),
    # 121: s07-e07-t06 | live | Walk to drum in exactly 9.58 seconds
    (5, 5, 5, "Place a pot at the far end of the room. Walk to it and hit it in exactly 10 seconds. No watches allowed. Closest to 10 seconds wins. Also judged on walk style."),
    # 122: s07-e08-t01 | prize | Bring in the creepiest thing
    (5, 5, 5, "Everyone finds the creepiest thing in the house — weird ornament, unsettling photo, something from the back of a drawer. Present in dim lighting. Group votes."),
    # 123: s07-e08-t02 | solo | Poke something unexpected out of a hole in roof
    (4, 3, 4, "Poke the most unexpected item through a doorway or over a partition. The reveal is everything. Group votes on most surprising object appearance."),
    # 124: s07-e08-t03 | solo | Treasure hunt — find hidden letters spelling a task
    (5, 4, 5, "Set up a mini treasure hunt around the house with clues leading to the next location. First to solve all clues and return wins. Great party game with prep."),
    # 125: s07-e08-t04 | solo | Compose best 30-second piece of music
    (5, 5, 5, "Everyone composes a 30-second song using only body percussion and voice. Perform live. Audience votes. No instruments required — just clapping, stomping, singing."),
    # 126: s07-e08-t05 | live | Bob/Pat/Kneel/Stew/Wane when you hear matching surnames
    (5, 5, 5, "Read out surnames of famous people. If it's a famous Bob, everyone bobs down. Famous Pat = pat your head. Wrong action = out. Fast-paced and hilarious."),
    # 127: s07-e09-t01 | prize | Bring in the most surprisingly beautiful thing
    (5, 5, 4, "Everyone finds something unexpectedly beautiful in the house — the pattern on a mug, a shadow, a household item from the right angle. Present poetically."),
    # 128: s07-e09-t02 | solo | Put most money in floating bowl without sinking it
    (5, 4, 5, "Float a small bowl in a pot of water. Take turns placing coins in it. If it sinks on your turn, you're out. Last player standing wins. Classic steady-hands game."),
    # 129: s07-e09-t03 | solo | Be photographed wearing fez in unusual situation. 8 weeks
    (5, 5, 2, "Requires 8 weeks. Not a party game. Could speed-run it: take a silly hat photo in the most unusual spot in the house within 5 minutes."),
    # 130: s07-e09-t04 (first) | solo | Hula hoop for one minute
    (5, 3, 4, "Needs a hula hoop. If you have one, everyone takes turns for one minute. Count rotations. Simple and physical. Great if available."),
    # 131: s07-e09-t04 (second) | solo | Improve hula-hooping over time
    (5, 3, 2, "Long-term improvement task. Doesn't work at a single party event."),
    # 132: s07-e09-t05 | solo | Find the satsuma in the socks
    (5, 4, 5, "Hide a small item in one of 20 socks. Everyone gets to put their hand in 3 socks and put 11 socks on their feet. First to find the hidden item wins."),
    # 133: s07-e09-t06 | team | Exactly 24-shot rally
    (5, 3, 4, "Teams volley a balloon back and forth, counting to exactly 24 hits. Overshoot or drop = restart. Most ambitious equipment (wooden spoons, books) gets bonus."),
    # 134: s07-e10-t01 (first) | prize | Bring in the most magnificent stationery
    (5, 5, 4, "Everyone raids the house for the most magnificent piece of stationery. Present with the gravitas of a fine art auctioneer. Group votes."),
    # 135: s07-e10-t01 (second) | special | Put on boiler suit and lie flat when siren sounds
    (5, 4, 4, "Set a random alarm on a phone. When it goes off mid-game, everyone must grab a specific item (a hat, a cushion) and lie flat. Slowest person loses a point."),
    # 136: s07-e10-t02 | solo | Find the boiled egg among raw ones
    (5, 5, 5, "Classic egg roulette. Everyone picks an egg and cracks it on their forehead. One is boiled, rest are raw. Visceral, hilarious, minimal equipment."),
    # 137: s07-e10-t03 | solo | Physically recreate a classic computer game. 1 hour
    (5, 4, 5, "Teams get 10 minutes to physically recreate a video game using household items. Tetris with cushions, Pac-Man with tape on the floor. Perform for the group."),
    # 138: s07-e10-t04 | solo | Tie yourself up as securely as possible
    (4, 4, 3, "A bit weird at a party. Could adapt: wrap yourself in cling film/tape. Partner has to free you. Slowest escape wins. Keep it light and silly."),
    # 139: s07-e10-t05 | live | Sausage or finger — blindfolded prodding game
    (5, 4, 5, "Classic Taskmaster game. Blindfolded, someone prods you with a sausage or finger. Guess wrong = out. Cheap, fast, always gets huge laughs. A perfect party game."),

    # ===== NZ S02 =====
    # 140: nz-s02-e01-t01 | prize | Bring in the best green thing
    (5, 5, 4, "Everyone finds the best item of a randomly chosen colour in the house. Present your find. Group votes on best interpretation."),
    # 141: nz-s02-e01-t02 | solo | Knock over pins from inside a caravan
    (3, 2, 3, "Needs a large outdoor space, a caravan, and bowling pins. Not practical for a house party."),
    # 142: nz-s02-e01-t03 | solo | Fly. Best flying wins. 30 min
    (4, 4, 5, "Everyone gets 5 minutes to demonstrate the best 'flying.' Jump off the sofa with a blanket cape, paper aeroplane from a balcony, creative interpretations welcome."),
    # 143: nz-s02-e01-t04 | solo | Brush Paul's teeth from furthest distance
    (5, 3, 4, "One person holds a toothbrush in their mouth. Everyone else devises a way to brush from as far away as possible — tape to a stick, string pulley. Furthest wins."),
    # 144: nz-s02-e01-t05 | live | Build toilet roll tower then throw shoe at rival's
    (5, 4, 5, "Build the tallest toilet roll tower in 60 seconds. Then everyone throws a shoe at someone else's tower. Tallest surviving tower wins. Quick and chaotic."),
    # 145: nz-s02-e02-t01 | prize | Bring in the hottest thing
    (5, 5, 4, "Everyone brings the 'hottest' thing — temperature, attractiveness, spiciness, all interpretations valid. Present your case. Group votes."),
    # 146: nz-s02-e02-t02 | solo | Float Brussels sprout from balcony. Longest float
    (4, 3, 4, "Drop a grape from the top of the stairs with a homemade parachute. Longest float time wins. 10 minutes to build your parachute from tissue/plastic bags."),
    # 147: nz-s02-e02-t03 | solo | Transform this room in 30 seconds of darkness
    (5, 5, 5, "Everyone preps for 2 minutes in the light. Then lights off for 30 seconds — transform the room. Lights on — most spectacular transformation wins."),
    # 148: nz-s02-e02-t04 | solo | Squirt sunscreen the furthest
    (4, 4, 4, "Line up outside or in a kitchen. Everyone gets a squeezy bottle (ketchup, mustard, mayo). Squirt it as far as possible in one squeeze. Furthest wins. Messy but quick."),
    # 149: nz-s02-e02-t05 | live | Paint portrait with electric toothbrushes
    (5, 3, 5, "Everyone paints a portrait of someone in the room using only a toothbrush as the brush. The subject describes themselves verbally. 3 minutes. Best likeness wins."),
    # 150: nz-s02-e03-t01 | prize | Bring in the most New Zealand thing
    (5, 5, 4, "Adapt to your own context — most [your city/country] thing. Everyone brings or describes the most locally iconic item. Group votes on truest representation."),
    # 151: nz-s02-e03-t02 | solo | Star in a one-minute multi-character film
    (5, 5, 5, "Everyone films a 1-minute movie on their phone playing ALL characters. Quick costume changes between shots. Most distinct characters wins. Screen for the group."),
    # 152: nz-s02-e03-t03 | team | Build castle from wheat biscuits
    (5, 4, 4, "Teams build the grandest structure from crackers/biscuits. Eat a dry cracker to earn more building materials. Dual challenge of construction and dry-mouth suffering."),
    # 153: nz-s02-e03-t04 | solo | Hop Scotch along hopscotch
    (4, 4, 5, "Hop along a taped hopscotch carrying a shot glass. Most liquid delivered to the end wins. Spillage is inevitable and hilarious."),
    # 154: nz-s02-e03-t05 | solo | Get photo of person in extraordinary location with specific pose
    (5, 5, 2, "Needs a long deadline. Not a single-evening game. Skip unless you have days of lead time."),
    # 155: nz-s02-e04-t01 | prize | Bring in the most impressive stolen item
    (5, 5, 5, "Everyone presents the most impressive thing they've ever 'borrowed.' Phone photo evidence acceptable. Best story of acquisition wins."),
    # 156: nz-s02-e04-t02 | solo | Get Swiss ball in kayak without getting wet
    (2, 1, 3, "Requires a kayak on water and an exercise ball. Not doable at a house party."),
    # 157: nz-s02-e04-t03 | solo | Perform Christmas song without banned words
    (5, 5, 5, "Assign a topic (birthday, holiday, Monday morning). Write and perform a 30-second song about it WITHOUT using 10 banned obvious words. Perform for the group."),
    # 158: nz-s02-e04-t04 | solo | Shoot chocolate fish into fishbowl, naming animals
    (5, 4, 5, "Throw sweets/grapes into a bowl from across the room. Must shout a different animal name with each throw. Run out of animals = disqualified. Most in the bowl wins."),
    # 159: nz-s02-e04-t05 | live | Briefcase bluffing — onions or nothing
    (5, 5, 5, "Put something secret in a bag — heavy or empty. Walk across the room nonchalantly. One person guesses heavy or empty. Wrong guess = guesser drinks. Bluffing game gold."),
    # 160: nz-s02-e05-t01 | prize | Bring in the best voucher
    (5, 5, 5, "Everyone writes a personal voucher for a service they'll actually provide — '1 free ride to airport,' 'homemade dinner.' Vote on most valuable."),
    # 161: nz-s02-e05-t02 | solo | Spill the beans — find the actual can of beans
    (5, 4, 4, "Hide one specific item among many decoys in a room. First to find and open the correct one wins. Simple scavenger hunt with a twist."),
    # 162: nz-s02-e05-t03 | solo | Make your hometown proud. 45 min
    (5, 5, 4, "Everyone gets 5 minutes to prepare and perform a tribute to their hometown — a song, a speech, a re-enactment. Group votes on most hometown-proud moment."),
    # 163: nz-s02-e05-t04 | solo | Make the loudest non-vocal noise
    (4, 5, 5, "No voice allowed. Make the loudest noise possible using household items. Everyone demonstrates. Neighbours may complain. Judge by crowd reaction."),
    # 164: nz-s02-e05-t05 | live | Pick weapon, pick snack, slice snack in half
    (5, 4, 5, "Everyone picks a random utensil and a random snack. Slice your snack as evenly in half as possible using your utensil. Most even split wins. Absurd combinations guaranteed."),
    # 165: nz-s02-e06-t01 | prize | Bring in the two most different things
    (5, 5, 5, "Everyone finds two items that are maximally different from each other. Present your pair. Group votes on which pair is most wildly contrasting."),
    # 166: nz-s02-e06-t02 | solo | Evacuate items from parachute while in rocking chair
    (4, 2, 3, "Needs a rocking chair and a parachute. Not standard party equipment. Could adapt: sit in a chair, feet off the ground, grab as many scattered items as possible."),
    # 167: nz-s02-e06-t03 | team | Create a diss track about the other team
    (5, 5, 5, "Teams of 2-3 write and perform a 1-minute diss track about the other team. 10 minutes prep. Perform live. Audience votes. Friendships will be tested."),
    # 168: nz-s02-e06-t04 | special | Dress as Abraham Lincoln and join video call ASAP
    (5, 3, 4, "Send a group text with a challenge: first person to send a photo of themselves dressed as a specific character using household items wins."),
    # 169: nz-s02-e06-t05 | live | Celebrity name chain — last letter becomes first letter
    (5, 5, 5, "Go round the circle naming celebrities. Each name must start with the last letter of the previous name. 10-second limit. Hesitate = out. Classic party word game."),
    # 170: nz-s02-e07-t01 | prize | Bring in the biggest bargain
    (5, 5, 5, "Everyone shows the best deal they've ever gotten — receipt photo, online order, thrift store find. Best bargain story wins."),
    # 171: nz-s02-e07-t02 | solo | Construct least appropriate wedding cake. 45 min
    (5, 4, 5, "Everyone builds the most inappropriate cake from kitchen supplies in 10 minutes. Stack bread, cover in ketchup, stick a candle in it. Most offensive cake wins."),
    # 172: nz-s02-e07-t03 | solo | Eat the grape — locked in caravan puzzle
    (5, 4, 4, "Set up a mini escape room — lock a grape in a box, hide the key. First to solve the puzzle and eat the grape wins. 10-minute time limit."),
    # 173: nz-s02-e07-t04 | solo | Make most extreme cup of tea
    (5, 4, 5, "Everyone makes the most extreme cup of tea possible in 5 minutes — hottest, spiciest, tallest, most ingredients. Then the host must taste each one."),
    # 174: nz-s02-e07-t05 | live | Lemonade roulette
    (5, 4, 5, "Shake one of two identical bottles of fizzy drink. Each player picks one and opens it. Get sprayed = eliminated. Simple, tense, and very wet."),
    # 175: nz-s02-e08-t01 | prize | Bring in the most nostalgia-inducing item
    (5, 5, 5, "Pull up the most nostalgic thing on your phone — old photo, a song, a text. Share with the group. Most collective 'awww' wins. Great bonding moment."),
    # 176: nz-s02-e08-t02 | solo | Build tallest onion tower + moving speech
    (5, 4, 4, "Stack fruit (oranges, apples) into the tallest tower. Deliver a moving speech while building for 15cm bonus height. Emotional architecture."),
    # 177: nz-s02-e08-t03 | solo | Time travel. 30 min
    (5, 5, 5, "Everyone has 5 minutes to demonstrate 'time travel' using whatever's available. Creative interpretations win — dress as a historical figure, show old photos, etc."),
    # 178: nz-s02-e08-t04 (first) | special | Secretly sabotage your team
    (5, 5, 4, "Give one person per team a secret saboteur role during a team task. If their team loses, the saboteur gets bonus points. If caught, they lose points."),
    # 179: nz-s02-e08-t04 (second) | team | Pack Paul's car with inflated objects
    (5, 4, 4, "Teams inflate as many balloons as possible and stuff them into a closet/cupboard. Most balloons in the space in 5 minutes wins. With a secret saboteur it's even better."),
    # 180: nz-s02-e08-t05 | live | Draw life-size self-portrait with nose in hole
    (5, 4, 5, "Tape paper to a wall. Cut a nose hole. Press your face into it and draw a life-size self-portrait around your face. 3 minutes. Most accurate wins."),
    # 181: nz-s02-e09-t01 | prize | Bring in the most edible-looking inedible item
    (5, 5, 4, "Everyone finds something in the house that looks delicious but isn't food — a soap, a candle, a stress ball. Most appetizing non-food wins."),
    # 182: nz-s02-e09-t02 | solo | Steal the Taskmaster's portrait — elaborate heist
    (5, 4, 5, "Hang a picture on the wall. One person guards it. Teams plan and execute a heist to steal it. Most elaborate/dramatic heist wins. Movie-style narration encouraged."),
    # 183: nz-s02-e09-t03 | solo | Walk specific distances in compass directions
    (4, 3, 3, "Needs outdoor space for precise distance walking. Indoors it's too cramped. Could do a simplified version with pacing out steps in a garden."),
    # 184: nz-s02-e09-t04 | solo | Take Paul on the perfect first date
    (5, 5, 5, "Everyone plans a 5-minute 'first date' for one willing participant. Set up ambiance, conversation topics, a snack. Most romantic wins. The 'date' scores each."),
    # 185: nz-s02-e09-t05 | solo | Re-enter room wearing tie in a brand new way
    (5, 5, 5, "Everyone gets a scarf or tie. Leave the room, re-enter wearing it in the most creative way possible. Not around the neck — headband, belt, sling. Most innovative wins."),
    # 186: nz-s02-e09-t06 | team | Recreate famous scenes from NZ history using only 4-letter words
    (5, 5, 5, "Teams act out famous scenes from history/movies, but can only speak in 4-letter words. Other team guesses. Most scenes guessed correctly wins."),
    # 187: nz-s02-e10-t01 | prize | Bring in the most futuristic thing
    (5, 5, 4, "Everyone finds the most futuristic item available — a smart device, a weird gadget, something shiny. Present it like a tech keynote. Group votes."),
    # 188: nz-s02-e10-t02 | solo | Get the most footage of Paul on camcorder
    (5, 4, 4, "One person hides. Everyone else has 2 minutes to find them and film as much footage as possible on their phone. Most seconds of footage wins."),
    # 189: nz-s02-e10-t03 | solo | Untie 4000 shoelaces
    (5, 3, 2, "Untangling thousands of shoelaces takes forever. Not a fun party activity. Skip unless you want to bore everyone."),
    # 190: nz-s02-e10-t04 | team | Educational puppet show
    (5, 4, 5, "Teams make sock puppets from socks and markers. 10 minutes to write and rehearse an educational puppet show. Perform for the group. Most educational wins."),
    # 191: nz-s02-e10-t05 | solo | Hold two milk bottles above microwaves as long as possible
    (5, 4, 3, "Hold two bottles at arm's length for as long as possible. Simple endurance test. Gets boring for spectators after 2 minutes."),
    # 192: nz-s02-e10-t06 | live | Make salad then undo it
    (5, 4, 5, "Everyone makes the best mini-salad in 60 seconds. Then — surprise — undo everything and put ingredients back in alphabetical order. Fastest undoer wins."),

    # ===== S19 =====
    # 193: s19-e01-t01 | prize | Bring in object that reminds you of school
    (5, 5, 5, "Everyone shares an object or phone photo that reminds them of school. Tell the story. Most evocative school memory wins. Great for nostalgia and bonding."),
    # 194: s19-e01-t02 | solo | Blindfolded, pour vinegar into fish tank
    (4, 3, 4, "Blindfolded, pour water into a cup from a bottle. Spillage = time penalty. Everyone tries. Towels ready. Quick and tense."),
    # 195: s19-e01-t03 | solo | Do something cool, then do it backwards
    (5, 5, 5, "Everyone films themselves doing a cool trick on their phone. Then film themselves doing it in reverse. Play the reverse video backwards. Best illusion wins."),
    # 196: s19-e01-t04 | live | Pealy-mpics — five pea-themed mini-events
    (5, 4, 5, "Run 5 quick mini-games with small objects. Find a hidden pea, build a tower, flick a pea the furthest. Most medals across all events wins."),
    # 197: s19-e02-t01 | prize | Bring in the snootiest thing
    (5, 5, 4, "Everyone finds the fanciest/most pretentious thing in the house. Present it with maximum snobbery. Pinky fingers raised. Group votes."),
    # 198: s19-e02-t02 | solo | Commentate on yourself achieving something tricky
    (5, 5, 5, "Record sports commentary on your phone about yourself doing something difficult (stack cups, catch grapes in mouth). Then actually do it. Best commentary + achievement wins."),
    # 199: s19-e02-t03 | team | Deliver 100 marbles on a plate while always sitting/jumping/clapping
    (5, 4, 5, "Teams deliver small items across the room while one person must always be sitting, one jumping, one clapping. Rotate roles constantly. Chaos is the point."),
    # 200: s19-e02-t04 | solo | Get most liquid in a can without leaving the room
    (5, 5, 4, "Stuck in one room, fill a cup with as much liquid as possible using whatever's available. Houseplant water, condensation from windows, get creative."),
    # 201: s19-e02-t05 | live | Choose mystery items then fit one inside the other
    (5, 4, 5, "Everyone blindly picks two items from bags. Then fit one item completely inside the other. Fastest wins. The random pairing creates hilarious impossibilities."),
    # 202: s19-e03-t01 | prize | Best thing for middle-aged man's bedside table
    (5, 5, 5, "Everyone picks a real item from the house for a specific person's bedside table. Present your case for why it's essential. Group votes on most thoughtful/funniest."),
    # 203: s19-e03-t02 | solo | Answer the cheese phone — find ringing phone in cheese
    (5, 3, 4, "Hide a ringing phone somewhere in the room. Everyone searches. Every time you move, someone plays a noise. Use only smell = double points. First to find it wins."),
    # 204: s19-e03-t03 | solo | Move cushions while avoiding Alex identifying cape colour
    (5, 4, 4, "Transport items between two bins while someone periodically opens their eyes to identify what you're wearing. Change outfit each trip to avoid detection."),
    # 205: s19-e03-t04 | solo | Paint picture but can only enter room for last 30 seconds
    (5, 4, 4, "Everyone plans a drawing for 3 minutes but can only actually draw for the last 30 seconds. Pre-plan elaborate paintings then execute at top speed. Compare results."),
    # 206: s19-e04-t01 | prize | Thing that least suits its name when shouted
    (5, 5, 5, "Everyone finds an object and shouts its name while the group looks at it. Most absurd mismatch between the shouted word and the gentle object wins. 'PILLOW!'"),
    # 207: s19-e04-t02 | solo | Put wetsuits on mannequins while tiptoeing and shushing
    (4, 2, 4, "Needs wetsuits and mannequins. Could adapt: dress a chair in as many items of clothing as possible while tiptoeing and whispering. Shushing every 20 seconds."),
    # 208: s19-e04-t03 | team | Convince other team things are the opposite
    (5, 5, 5, "Teams take turns lying convincingly about everyday facts. Is this coffee hot or cold? Is this bag heavy or light? The other team guesses truth or lie. Best actors win."),
    # 209: s19-e04-t04 | solo | Figure out why the light bulb turns on
    (5, 4, 4, "Set up a mystery — something in the room changes based on a hidden rule. First to figure out the pattern wins. Good puzzle-solving entertainment."),
    # 210: s19-e04-t05 | live | Front ham — strategic sock washing line game
    (5, 4, 4, "Needs a washing line and colour-coded items. Each turn remove 3 items and add 1. If your secret colour disappears, you're out. Strategic and tense."),
    # 211: s19-e05-t01 | prize | Best object to bequeath as revenge in a Will
    (5, 5, 5, "Everyone picks the most annoying item in the house to give to someone specific. Explain who'd receive it and why it's the perfect revenge. Dark humour wins."),
    # 212: s19-e05-t02 | solo | Least annoying person round the campfire
    (5, 5, 5, "Everyone performs a folk song, ghost story, or spoken word poem about an assigned topic. Least annoying performer wins. Deliberately bad performances are the best."),
    # 213: s19-e05-t03 | solo | Draw a monster behind you from a car, honk at lollipop ladies
    (4, 2, 3, "Needs a car and outdoor space with interruptions. Too elaborate for a house party. The concept is good but the setup isn't."),
    # 214: s19-e05-t04 | solo | Shorten pencils then recall everything you said
    (5, 5, 4, "Two-part memory task. Do a simple activity while chatting. Then recall every word you said. Great for testing who's been paying attention at the party."),
    # 215: s19-e05-t05 | live | Pop balloon when you hear its colour in a story
    (5, 4, 5, "Everyone holds coloured balloons. Read a story — when a colour is mentioned, pop that balloon. Last to pop = eliminated. Pop wrong colour = eliminated. Fast and loud."),
    # 216: s19-e05-t06 | special | Make as many holes in paper as possible with one hole punch use
    (5, 5, 5, "Everyone gets a sheet of paper and a hole punch. One squeeze only. Most holes wins. Fold the paper cleverly to multiply your holes. Quick and clever."),
    # 217: s19-e06-t01 | prize | Bring in the thing nicest to open
    (5, 5, 4, "Everyone finds the most satisfying thing to open — a jar, a box, an envelope. Group tests each one. Most satisfying opening sensation wins."),
    # 218: s19-e06-t02 | solo | Work out what's on Alex's head via yes/no questions
    (5, 5, 5, "Put a mystery object on someone's head. They ask yes/no questions to figure out what it is. Fewest questions wins. Others watch and try not to give it away."),
    # 219: s19-e06-t03 | team | Make yourselves look like a family, film home video
    (5, 5, 5, "Teams disguise themselves as a family unit using whatever's available. Film a 30-second 'family home video.' Best family impression wins. Wigs and accents encouraged."),
    # 220: s19-e06-t04 | solo | Teach Alex a lesson he'll never forget
    (5, 5, 5, "Everyone gets 3 minutes to teach the group something memorable — a weird fact, a skill, an unsettling truth. Most unforgettable lesson wins. Knowledge is power."),
    # 221: s19-e06-t05 | live | Don't blow the last thing off the table
    (5, 5, 5, "Place 5 lightweight items on a table. Take turns blowing one item off. Must blow at least one. Blow the last one off = you lose. Simple breath-powered strategy game."),
    # 222: s19-e07-t01 | prize | Bring in the biggest anti-climax
    (5, 5, 5, "Everyone builds up the biggest anticlimax — elaborate setup, disappointing payoff. Best gap between expectation and reality wins."),
    # 223: s19-e07-t02 | solo | Puzzle/code-breaking — what's in the yellow box
    (5, 4, 4, "Set up a multi-clue puzzle around the house. First to solve the chain and identify the hidden object wins. Requires prep but very engaging."),
    # 224: s19-e07-t03 | solo | Eat yogurt with most/least dignity
    (5, 5, 5, "Everyone eats a snack with either maximum dignity or zero dignity — they choose. Most extreme performance in either direction wins. Fork and knife for a grape vs. face in a bowl."),
    # 225: s19-e07-t04 | solo | Fill vase with 6 litres via obstacle routes
    (4, 3, 3, "Needs outdoor space and specific equipment. Too elaborate for a house party setup. The dual-route concept is great but hard to reproduce."),
    # 226: s19-e07-t05 | team | Get balls into bucket through fence using spoons
    (5, 4, 5, "Set up a barrier (sofa, table on its side). Teams use spoons to pass balls over/through the barrier into a bucket. Most balls in 5 minutes wins. Frantic and fun."),
    # 227: s19-e08-t01 | prize | Best object borrowed from a fairly close friend
    (5, 5, 5, "Everyone shows something they borrowed from a friend and never returned. Confess the story. Group votes on best long-term 'borrowed' item."),
    # 228: s19-e08-t02 | solo | Knock over skittles, final one at exactly 10 min
    (4, 3, 3, "Needs bowling pins and precise timing equipment. The timing aspect is clever but hard to set up at a party."),
    # 229: s19-e08-t03 | team | Write 3 words, paint scene on spinning turntable, teammate guesses
    (5, 3, 5, "One person writes 3 words. Their partner draws a scene on a spinning plate/lazy susan to communicate those words. Audience guesses too. Rotating art is hilarious."),
    # 230: s19-e08-t04 | live | Higher or lower with personal facts
    (5, 5, 5, "Go around the room with personal facts — shoe size, countries visited, speeding tickets. Each person guesses if the next person's number is higher or lower. Revealing and fun."),
    # 231: s19-e09-t01 | prize | Most satisfying jelly mould shape
    (5, 5, 4, "Everyone finds an object that would make the best jelly mould. Present your mould and describe the resulting jelly. Most satisfying imagined jelly wins."),
    # 232: s19-e09-t02 | solo | Place something somewhere surprising
    (5, 5, 5, "Everyone secretly hides an object somewhere surprising in the house. The host tours the house reacting to each discovery. Biggest genuine reaction wins."),
    # 233: s19-e09-t03 | team | Create dynamic duo costumes with Alex
    (5, 4, 5, "Pairs create matching superhero costumes from household items in 10 minutes. Then perform a 1-minute dynamic duo routine. Best act wins."),
    # 234: s19-e09-t04 | solo | Conquer the multitask — multiple rooms, multiple sub-tasks
    (5, 4, 4, "Set up 4-5 mini-tasks in different rooms (drink this, wear that, answer a question, do 5 star jumps). Fastest to complete all of them wins. Requires prep but great payoff."),
    # 235: s19-e09-t05 | team | Word-association speed game with button/timer
    (5, 5, 5, "Teams take turns naming words in a category. Slap the table to pass to the other team. Hesitate for 3 seconds = you lose. Fast-paced word association duel."),
    # 236: s19-e10-t01 | prize | Thing most likely to make you do a double take
    (5, 5, 5, "Everyone sets up a visual double-take somewhere in the house — something that looks normal at first glance but is deeply wrong. Group tours. Best delayed reaction wins."),
    # 237: s19-e10-t02 | solo | Fill yellow box with sand, carrying all touched boxes
    (3, 2, 3, "Needs sand and multiple boxes scattered around a property. Too elaborate for indoors. The concept of accumulating burdens is great but needs space."),
    # 238: s19-e10-t03 | solo | Powerful pose with objects, hold for 10 minutes
    (5, 4, 3, "Strike a powerful pose and hold it for 10 minutes. Endurance test — dramatic but gets dull for spectators. Shorten to 3 minutes and add distractions."),
    # 239: s19-e10-t04 | team | Run a drive-through restaurant for bike-riding customers
    (4, 3, 5, "Teams set up a restaurant in one room. Customers order ridiculous food. Teams must prepare and serve. Best dining experience wins. Needs prep but brilliant."),
    # 240: s19-e10-t05 | live | Get carrots in bucket without using hands
    (5, 4, 5, "Scatter items on the floor. Get them into a bucket without using hands. Mouth, feet, teamwork. 100 seconds. Fastest collection wins."),

    # ===== S20 =====
    # 241: s20-e01-t01 | prize | Bring in a very soft thing beneficial for Greg
    (5, 5, 4, "Everyone finds the softest item in the house and argues why it would benefit a specific person. Most convincing soft-sell wins."),
    # 242: s20-e01-t02 | solo | Honk the horn — QR code scavenger task
    (5, 4, 4, "Hide a QR code somewhere. First person to find and scan it gets a task. Timer starts from your first word, so silence is golden. Modern and clever."),
    # 243: s20-e01-t03 | solo | Roll object onto target from behind a line
    (5, 4, 4, "Tape a target on the floor across the room. Roll objects (oranges, balls, cans) from behind a line. Closest to center wins. Bocce/bowls in your living room."),
    # 244: s20-e01-t04 | solo | Do something behind curtain that sounds disgusting but is nice
    (5, 5, 5, "One person goes behind a curtain/door and makes sounds that seem disgusting. The group guesses what they're actually doing. Most deceptive nice-sound-disgusting wins."),
    # 245: s20-e01-t05 | live | Guess how many things Alex has on him
    (5, 5, 5, "One person goes behind a screen and puts on random items. Others guess how many things they're wearing/carrying. Worst guess each round eliminated."),
    # 246: s20-e02-t01 | prize | Bring in object hardest to describe
    (5, 5, 5, "Everyone finds the most indescribable object in the house. Try to describe it to the group. If nobody can sum it up, you win."),
    # 247: s20-e02-t02 | solo | Identify 5 hidden things using only one sense
    (5, 4, 5, "Hide 5 items behind a screen. Everyone picks one sense (touch = 3 pts each, smell = 4, sound = 5). Identify as many as possible. Higher risk = higher reward."),
    # 248: s20-e02-t03 | team | Hook a duck, get a superpower, use it in team task
    (5, 4, 5, "Write silly superpowers on cards. Each person draws one randomly. Teams then complete a task but must roleplay their assigned superpower throughout."),
    # 249: s20-e02-t04 | solo | Take most surprising thing out of this bag
    (5, 5, 5, "Give everyone a big bag and 5 minutes. Put something in and produce it with maximum theatricality. Most surprising Mary Poppins reveal wins."),
    # 250: s20-e02-t05 | live | (continuation/discussion — no real task)
    (5, 5, 3, "No distinct task described. Cannot adapt meaningfully."),
    # 251: s20-e03-t01 | prize | Bring in thing you were least likely to bring from home
    (5, 5, 5, "Everyone picks the most unlikely item they'd normally bring to a party. Most unexpected object wins. The story matters as much as the item."),
    # 252: s20-e03-t02 | solo | Make model of mascot by peeking in 2 of 5 tents
    (5, 4, 4, "Show a picture for 5 seconds. Everyone sculpts it from Play-Doh or draws it from memory. Only allowed 2 more peeks. Most accurate wins."),
    # 253: s20-e03-t03 | team | Discover name of mystery person by asking yes/no questions
    (5, 5, 5, "One person thinks of a celebrity. Teams take turns asking one yes/no question each. First team to guess the name wins. Classic 20 questions with team tactics."),
    # 254: s20-e03-t04 | solo | Create snakes and steps board with custom rules
    (5, 4, 4, "Everyone designs one section of a board game with custom rules (snake, ladder, mystery square). Combine them into one board and play it. Collaborative game design."),
    # 255: s20-e03-t05 | live | Flip cup triangle upside down following layer instructions
    (5, 5, 5, "Stack cups in a pyramid. Flip the entire structure upside down following specific handicap rules (one hand behind back, one eye shut). Fastest wins."),
    # 256: s20-e04-t01 | prize | Best birthday gift
    (5, 5, 4, "Everyone wraps up a gift from things found in the house. Present it with wrapping, ribbon, and a card. Most gorgeous presentation wins."),
    # 257: s20-e04-t02 | solo | Guess Alex's number via yes/no questions with escalating surprise
    (5, 5, 5, "One person thinks of a number 1-100. Others ask yes/no questions but must show increasingly exaggerated surprise at each answer. Best performance + fewest questions wins."),
    # 258: s20-e04-t03 | solo | Horse race controlled by eating olives/grapes
    (5, 4, 5, "Set up a tabletop horse race. Eat an olive = advance 2 spaces. Eat a grape = advance 1. Spit a grape onto a target = advance 3. Edible racing madness."),
    # 259: s20-e04-t04 | special | Remove shower cap by inflating balloon
    (5, 4, 5, "Everyone wears a shower cap (or paper hat). Blow up a balloon inside it until it pops off. Fastest wins. Cheap, fast, hilarious tiebreaker."),
    # 260: s20-e05-t01 | prize | Possession that would confuse a future archaeologist if buried with you
    (5, 5, 5, "Everyone picks the item that would most confuse future archaeologists. Explain why. Most baffling tomb offering wins."),
    # 261: s20-e05-t02 | solo | Pull something across obstacles using string
    (4, 3, 3, "Needs a long outdoor course with obstacles. Too elaborate for a house party. The ball-firing machine alone rules this out."),
    # 262: s20-e05-t03 | team | Make things genuinely awkward. 20 min
    (5, 5, 5, "Teams have 5 minutes to create the most genuinely awkward moment. Perform for the group. Most uncomfortable (but consenting) scenario wins."),
    # 263: s20-e05-t04 | solo | Finger painting of person on phone, only 4-letter words
    (5, 5, 5, "Call a friend. Describe a person in the room using only 4-letter words. Your friend draws based on your description. Most accurate portrait wins."),
    # 264: s20-e05-t05 | live | Prisoner's dilemma with chocolate ducks
    (5, 5, 5, "Prisoner's dilemma with shots instead of chocolate ducks. Everyone decides secretly whether to drink or refuse. Reveal together. Only cooperator who eats alone wins big."),
    # 265: s20-e06-t01 | prize | Thing Greg would most like to see Alex wearing
    (5, 5, 4, "Everyone assembles an outfit for a specific person from items in the house. That person must wear the winning outfit. Fashion disaster competition."),
    # 266: s20-e06-t02 | solo | Cut a single string to cause greatest effect
    (5, 4, 4, "Everyone gets string, scissors, and 10 minutes to set up a Rube Goldberg-style chain reaction. Cut one string to trigger the whole thing. Most dramatic effect wins."),
    # 267: s20-e06-t03 | solo | Write 10-word autobiography then communicate from a bridge
    (5, 5, 5, "Write a 10-word life story. Then communicate it to the group without speaking — mime, props, drawings only. Most accurately guessed autobiography wins."),
    # 268: s20-e06-t04 | solo | Wear flippers — slowest wins, but hidden penalty envelopes
    (5, 3, 4, "Give everyone flippers (or oven mitts). Slowest to put them on wins. But hidden notes keep halving your time for rule violations. Tricky and funny."),
    # 269: s20-e06-t05 | live | Find age of mystery person via yes/no questions, limited numbers
    (5, 5, 5, "Someone hides their age. Others ask yes/no questions but can only say two numbers total. Most strategic questioning wins. Deduction under pressure."),
    # 270: s20-e07-t01 | prize | Best thing you can ride or rip
    (5, 5, 4, "Everyone finds something they can ride OR rip. Demonstrate. Group votes on best ride or most satisfying rip."),
    # 271: s20-e07-t02 | team | Steal statue of Archimedes — heist task
    (5, 4, 5, "One person guards an object. Teams plan a heist using surveillance (phone screen). Alarms = phones vibrating, codes = sticky notes. Most elaborate steal wins."),
    # 272: s20-e07-t03 | solo | Technicolor mouth dribble art
    (3, 3, 4, "Dribble coloured drinks from your mouth onto paper below. Messy but artistic. Use food colouring in water. Lay newspaper everywhere. Best splatter art wins."),
    # 273: s20-e07-t04 | solo | Bop Alex on head exactly 63 times shouting food names
    (5, 4, 5, "Whac-a-mole with real people. Multiple heads pop up over a sofa. Bop the right one while shouting a food name each time. Reach exactly the target number."),
    # 274: s20-e07-t05 | live | Avoid the Taskmaster's big ball — dodge from circle
    (5, 4, 5, "Everyone stands on a spot facing away from the thrower. The thrower rolls a ball at them — one step per round to dodge. Last person not hit wins. Tense and physical."),
    # 275: s20-e08-t01 | prize | Best thing with a surprise aspect
    (5, 5, 5, "Everyone presents something with a hidden surprise — a box within a box, a secret compartment, a twist. Best genuine surprise wins."),
    # 276: s20-e08-t02 | solo | Go to lobby on horn, return on whistle, answer question
    (5, 5, 4, "One person sits in another room. A horn sounds — they run back and answer a quiz question within 30 seconds. Multiple rounds. Most correct answers wins."),
    # 277: s20-e08-t03 | solo | Paint portrait of Taskmaster from a balcony
    (4, 3, 4, "Paint a portrait from above — tape paper to the floor, drop/drip paint from standing height. Everyone does it simultaneously. Most recognizable overhead painting wins."),
    # 278: s20-e08-t04 | solo | Cumulative endurance poses while reading words
    (5, 5, 4, "Stand on one leg, finger in ear, hand on head — accumulate silly poses while reading tongue-twisters aloud. Last person maintaining all poses wins."),
    # 279: s20-e08-t05 | live | Charades with extra link — telephone game
    (5, 5, 5, "Charades telephone. One person sees the phrase, acts it to the next, who acts it to the next, who guesses. The degradation of the message is comedy gold."),
    # 280: s20-e09-t01 | prize | Most respected item that retains credibility in high-pitched voice
    (5, 5, 5, "Everyone presents a serious/respected item but must describe it in a squeaky high-pitched voice. If it still sounds credible, you win. Guaranteed laughter."),
    # 281: s20-e09-t02 | solo | Build brick tower on trolley, push down slope
    (3, 2, 3, "Needs a trolley, bricks, and a slope. Too much specialist equipment for a house party. The screaming-while-peeking twist is great but can't offset the logistics."),
    # 282: s20-e09-t03 | solo | Make jockey weigh same as Alex using 2 scale readings
    (5, 3, 4, "Estimate someone's weight using only 2 readings from a bathroom scale. Dress a mannequin/pillow to match. Closest without going over wins. Needs a scale."),
    # 283: s20-e09-t04 | solo | Most fantastic 15-second film featuring your face
    (5, 5, 5, "Everyone films a 15-second masterpiece on their phone featuring their face in close-up the entire time. Screen them for the group. Oscar-worthy selfie cinema."),
    # 284: s20-e09-t05 | live | Draw bottom half of face/body to match shouted character
    (5, 5, 5, "Everyone holds a card over their forehead. Draw the lower half of a character shouted by the host. Reveal the composite face. 'Henry VIII on a horse' meets your chin."),
    # 285: s20-e10-t01 | prize | Bring in your very best tube
    (5, 5, 4, "Everyone finds the best tube in the house — toilet roll tube, a Pringle can, a rolled-up magazine. Present with gravitas. Best tube wins."),
    # 286: s20-e10-t02 | team | Make same-looking drinks as teammate independently
    (5, 5, 5, "Separated teammates must independently make drinks that look identical without communicating. Compare side by side. Most similar pair wins. Tests how well you know each other."),
    # 287: s20-e10-t03 | solo | Drink apple juice without touching or moving the cup
    (5, 5, 5, "Put a drink on the table. Drink it without touching or moving the cup. Straws, slurping, tilting — no hands on the cup. Fastest wins. Simple Pythagoras puzzle."),
    # 288: s20-e10-t04 | solo | Make water squirt out of you in a surprising way
    (4, 4, 5, "Everyone rigs themselves to squirt water from a surprising place. One person examines each player and guesses where the water will come from. Most surprising squirt wins."),
    # 289: s20-e10-t05 | live | Wibble/bibble/bam response game
    (5, 5, 5, "The host says 'wibble,' 'bibble,' or 'bam' — each maps to a different response. Hesitate or get it wrong = out. Speed increases each round. A perfect party warm-up."),
]

def main():
    with open("tasks-index-scored.json") as f:
        tasks = json.load(f)

    assert len(tasks) == len(SCORES), f"Expected {len(tasks)} scores, got {len(SCORES)}"

    changes = {"safety": 0, "equipment": 0, "group_fun": 0, "party_score": 0}
    strong_disagreements = []

    for i, task in enumerate(tasks):
        safety, equipment, group_fun, party_notes = SCORES[i]
        party_score = safety * equipment * group_fun
        party_adaptable = party_score >= 48

        old_score = task.get("party_score", 0)

        # Track changes
        if task.get("safety") != safety:
            changes["safety"] += 1
        if task.get("equipment") != equipment:
            changes["equipment"] += 1
        if task.get("group_fun") != group_fun:
            changes["group_fun"] += 1
        if old_score != party_score:
            changes["party_score"] += 1

        # Track strong disagreements (score changed by more than 40 in either direction)
        if abs(old_score - party_score) >= 40:
            strong_disagreements.append({
                "id": task["id"],
                "task": task["task_description"][:80],
                "old_score": old_score,
                "new_score": party_score,
                "reason": party_notes
            })

        # Update task
        task["safety"] = safety
        task["equipment"] = equipment
        task["group_fun"] = group_fun
        task["party_score"] = party_score
        task["party_adaptable"] = party_adaptable
        task["party_notes"] = party_notes

        # Remove old keyword-scorer notes
        for key in ["safety_note", "equipment_note", "group_fun_note"]:
            task.pop(key, None)

    # Save
    with open("tasks-index-llm-scored.json", "w") as f:
        json.dump(tasks, f, indent=2)
    print("Saved tasks-index-llm-scored.json")

    # Summary
    print(f"\n{'='*60}")
    print("SCORE CHANGES FROM KEYWORD VERSION:")
    print(f"{'='*60}")
    for field, count in changes.items():
        print(f"  {field}: {count}/{len(tasks)} tasks changed")

    # Top 30
    ranked = sorted(enumerate(tasks), key=lambda x: x[1]["party_score"], reverse=True)
    print(f"\n{'='*60}")
    print("TOP 30 PARTY TASKS:")
    print(f"{'='*60}")
    for rank, (idx, task) in enumerate(ranked[:30], 1):
        print(f"  {rank:2d}. [{task['party_score']:3d}] {task['id']} — {task['task_description'][:70]}")
        print(f"      {task['party_notes'][:90]}")

    # Strong disagreements
    print(f"\n{'='*60}")
    print(f"STRONG DISAGREEMENTS WITH KEYWORD SCORER ({len(strong_disagreements)} tasks):")
    print(f"{'='*60}")
    for d in sorted(strong_disagreements, key=lambda x: abs(x["old_score"] - x["new_score"]), reverse=True):
        direction = "UP" if d["new_score"] > d["old_score"] else "DOWN"
        print(f"  {d['id']}: {d['old_score']} -> {d['new_score']} ({direction})")
        print(f"    Task: {d['task']}")
        print(f"    Note: {d['reason'][:100]}")

    # Stats
    adaptable = sum(1 for t in tasks if t["party_adaptable"])
    print(f"\n{'='*60}")
    print(f"OVERALL: {adaptable} of {len(tasks)} tasks are party-adaptable (score >= 48)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
