
# Historical Blackjack Analysis in Python

In a ridiculous deep dive I wrote Python code to check the hand calculations done by Baldwin, Cantey, Maisel, and McDermott to evaluate the expected winnings of their optimum blackjack strategy[1], and then the more exact calculations done by Thorp using a computer[4,5].

The tl;dr is that Thorp's more exact +0.09% appears to be correct and the approximate -0.6% reported in the paper by Baldwin et al. should have been -0.3% (as communicated to Thorp by Cantey after the paper was published).

DISCLAIMER: This is not cutting edge analysis and the analyzed strategy is not the best currently known. You should assume my code is riddled with bugs and that you will lose money if you play blackjack for money using anything you read here.


## Timeline

### 1956

Roger Baldwin, Wilbert Cantey, Herbert Maisel, and James McDermott,
four U.S. Army poker buddies stationed at Aberdeen Proving Ground,
published "The Optimum Strategy in Blackjack" in the Journal of the American Statistical Association in 1956[1].

Roger Baldwin, who had just earned a master's degree in statistics, worked out the formulas to solve for the optimum blackjack strategy in 1953 and enlisted the help of the others, who all had master's degrees in mathematics, to perform the calculations on electromechanical desk calculators in their spare time over a period of two years.

They calculated that, using their strategy, the player's expected winnings were -0.6%:

> The player's disadvantage in blackjack stems entirely from the rule that if both the player and dealer bust,
> the dealer wins. The player's disadvantage is smaller than in other popular house games such as craps and roulette
> where his mathematical expectation is, at best, -1.4%. Furthermore, the optimum strategy is considerably superior
> to many common strategies. The player, for example, who follows the strategy recommended by Culbertson et al. has
> an expectation of -3.6%. The player who mimics the dealer, drawing to 16 or less, standing on 17 or more, never
> doubling down or splitting pairs, has an expectation of -5.6%.

Note: All expected winnings have been converted to percentages.

### 1957

In 1957 Baldwin, Cantey, Maisel, and McDermott published their optimum blackjack strategy, along with a primitive card counting scheme, in the book "Playing Blackjack to Win"[3].

### 1961

Edward Thorp, who had just earned a Ph.D. in mathematics, came across their work in 1958 and checked their calculations on an IBM 704 computer at MIT.
He published his findings in "A Favorable Strategy for Twenty-One" in the Proceedings of the National Academy of Sciences in 1961[4]:

> Our calculations are similar to those outlined in Baldwin et al., but there are some very important changes.
> First, a high-speed computer was programmed to find the player's best possible strategy and the corresponding
> expectation. The electronic calculator enabled us to dispense with many of the approximations that were needed
> by Baldwin et al. to reduce the calculations to desk computer size. This led to noticeable improvements in results.
> In particular, the player's expectation for a complete deck was found to be a startling -0.21%.
> (Baldwin et al. give -0.62%)

### 1966

Thorp went on to extend their work and published his own basic strategy along with several card counting systems in the book "Beat the Dealer" in 1966[5].
In that book he casually mentioned in a footnote:

> Mr. Wilbert E. Cantey has told us that an error in arithmetic, discovered after
> "The Optimum Strategy in Blackjack" and "Playing Blackjack to Win" were published,
> shows that the figure given for the house advantage should have been 0.32 per cent,
> rather than 0.62 per cent.
> The correct figure for their strategy is a *player* advantage of 0.09%


## Baldwin's Original Calculations

[See baldwinpaper.py for full details]

Roger Baldwin's formulas make use of two simplifying approximations:
1. the dealer and player card draw probabilities are calculated independently
2. beyond the first two or three cards in a hand, the probability of drawing any card is based on a full deck (1/13 for Ace to 9 and 4/13 for 10 cards)

The basic idea is to first calculate the probability of all of the possible dealer totals (17 to 21, natural 21, and bust) and then use those probabilities to evalute the expected winnings for the totals that the player stands on according to a strategy (taking into account any splitting, doubling, or hitting along the way).
All of this is done once for each possible dealer face up card and the results are then combined to calculate the overall expected winnings for the strategy.
The optimum strategy was solved for by maximizing the expected winnings at each decision point.

They solved for a one deck game where the dealer stands on hard or soft 17 and re-splitting is not allowed.

Here is a summary of the optimum strategy from their paper:

* Split pairs marked with S for dealer face up card

**Pair / Dealer Face Up Card**
|Pair|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|A|S|S|S|S|S|S|S|S|S|S|
|10| | | | | | | | | | |
|9|S|S|S|S|S| |S|S| | |
|8|S|S|S|S|S|S|S|S|S|S|
|7|S|S|S|S|S|S|S| | | |
|6|S|S|S|S|S|S| | | | |
|5| | | | | | | | | | |
|4| | | |S| | | | | | |
|3|S|S|S|S|S|S| | | | |
|2|S|S|S|S|S|S| | | | |

* Double totals marked with D for dealer face up card

**Total / Dealer Face Up Card**
|Hard Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|11|D|D|D|D|D|D|D|D|D| |
|10|D|D|D|D|D|D|D|D| | |
|9|D|D|D|D|D| | | | | |

|Soft Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|18| | |D|D|D| | | | | |
|17| |D|D|D|D| | | | | |
|16| | | |D|D| | | | | |
|15| | | |D|D| | | | | |
|14| | | |D|D| | | | | |
|13| | | |D|D| | | | | |
|12| | | |D| | | | | | |

* Stand on totals marked with S (or greater) for dealer face up card

**Total / Dealer Face Up Card**
|Hard Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|17| | | | | |S|S|S|S|S|
|16| | | | | | | | | | |
|15| | | | | | | | | | |
|14| | | | | | | | | | |
|13|S|S| | | | | | | | |
|12| | |S|S|S| | | | | |

|Soft Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|19| | | | | | | |S|S| |
|18|S|S|S|S|S|S|S| | |S|

And here are the expected winnings from the paper for the strategy:

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.090|0.123|0.167|0.218|0.230|0.148|0.056|-0.043|-0.176|-0.363|
**Overall:** -0.006

But remember Thorp's footnote with Cantey's correction that this value should be -0.0032 instead of -0.0062.

Here are the results from my Python code:

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.0949|0.1255|0.1681|0.2138|0.2256|0.1462|0.0580|-0.0368|-0.1694|-0.3599|

**Overall:** -0.0033

Which is very close to Cantey's corrected value.

Keep in mind that Baldwin et al. did their calculations by hand on desk calculators over a period of two years,
so it's not surprising that a few errors slipped through.

That said, they included their table probabilities for all of the possible dealer totals (17 to 21, natural 21, and bust),
calculated by dealer face up card, and they match very closely with my Python code:

**Dealer Face Up Card / Dealer Total**
| |17|18|19|20|21|Natural|Bust|
|--|--|--|--|--|--|--|--|
|2|0.141781|0.134885|0.131432|0.123829|0.119581|0.000000|0.348492|
|3|0.133533|0.133052|0.126197|0.122563|0.114903|0.000000|0.369751|
|4|0.132206|0.116037|0.122553|0.117930|0.114292|0.000000|0.396983|
|5|0.121374|0.124511|0.117753|0.105446|0.107823|0.000000|0.423092|
|6|0.167625|0.107233|0.108018|0.101260|0.098364|0.000000|0.417499|
|7|0.372743|0.139017|0.077841|0.079409|0.073437|0.000000|0.257552|
|8|0.131202|0.363359|0.129634|0.068457|0.070026|0.000000|0.237322|
|9|0.122256|0.104217|0.357550|0.122256|0.061079|0.000000|0.232643|
|10|0.114756|0.113186|0.114756|0.328873|0.036324|0.078431|0.213674|
|A|0.128147|0.131284|0.129716|0.131284|0.051284|0.313725|0.114560|

Conditional probability when no dealer natural:

**Dealer Face Up Card / Dealer Total**
| |17|18|19|20|21|Natural|Bust|
|--|--|--|--|--|--|--|--|
|10|0.124522|0.122819|0.124522|0.356862|0.039415|0.000000|0.231859|
|A|0.186728|0.191299|0.189015|0.191299|0.074728|0.000000|0.166930|

The corresponding tables generated by my Python code:

**Dealer Face Up Card / Dealer Total**
| |17|18|19|20|21|Natural|Bust|
|--|--|--|--|--|--|--|--|
|2|0.141782|0.134885|0.131433|0.123829|0.119580|0.000000|0.348490|
|3|0.133534|0.133052|0.126197|0.122563|0.114903|0.000000|0.369751|
|4|0.132206|0.116037|0.122553|0.117931|0.114292|0.000000|0.396982|
|5|0.121374|0.124511|0.117754|0.105446|0.107823|0.000000|0.423092|
|6|0.167625|0.107233|0.108017|0.101260|0.098364|0.000000|0.417499|
|7|0.372743|0.139018|0.077841|0.079410|0.073437|0.000000|0.257552|
|8|0.131202|0.363359|0.129634|0.068457|0.070026|0.000000|0.237322|
|9|0.122256|0.104216|0.357550|0.122256|0.061079|0.000000|0.232643|
|10|0.114756|0.113187|0.114756|0.328873|0.036324|0.078431|0.213673|
|A|0.128147|0.131284|0.129715|0.131284|0.051284|0.313725|0.114560|

Conditional probability when no dealer natural:

**Dealer Face Up Card / Dealer Total**
| |17|18|19|20|21|Natural|Bust|
|--|--|--|--|--|--|--|--|
|10|0.124522|0.122820|0.124522|0.356862|0.039416|0.000000|0.231858|
|A|0.186728|0.191300|0.189014|0.191300|0.074728|0.000000|0.166930|

Disagreements between the paper and my Python code:

**Dealer Face Up Card / Dealer Total**
| |17|18|19|20|21|Natural|Bust|
|--|--|--|--|--|--|--|--|
|2|0.000001|0.000000|0.000001|0.000000|-0.000001|0.000000|-0.000002|
|3|0.000001|0.000000|0.000000|0.000000|0.000000|0.000000|0.000000|
|4|0.000000|0.000000|0.000000|0.000001|0.000000|0.000000|-0.000001|
|5|0.000000|0.000000|0.000001|0.000000|0.000000|0.000000|0.000000|
|6|0.000000|0.000000|-0.000001|0.000000|0.000000|0.000000|0.000000|
|7|0.000000|0.000001|0.000000|0.000001|0.000000|0.000000|0.000000|
|8|0.000000|0.000000|0.000000|0.000000|0.000000|0.000000|0.000000|
|9|0.000000|-0.000001|0.000000|0.000000|0.000000|0.000000|0.000000|
|10|0.000000|0.000001|0.000000|0.000000|0.000000|0.000000|-0.000001|
|A|0.000000|0.000000|-0.000001|0.000000|0.000000|0.000000|0.000000|

Disagreements in conditional probability when no dealer natural:

**Dealer Face Up Card / Dealer Total**
| |17|18|19|20|21|Natural|Bust|
|--|--|--|--|--|--|--|--|
|10|0.000000|0.000001|0.000000|0.000000|0.000001|0.000000|-0.000001|
|A|0.000000|0.000001|-0.000001|0.000001|0.000000|0.000000|0.000000|

## More Accurate Calculations (ala Thorp Paper)

[See ewcalc.py for full details]

In his 1961 paper[4], Thorp says that using a computer he was able to dispense with some of Baldwin's approximations and compute a more exact result of -0.21%.
He doesn't say which approximations he dispensed with, but the low hanging fruit would have been to keep the independent evaluation of dealer and player probabilities, but use exact card draw probabilities throughout those calculations (instead of falling back to 1/13 for Ace to 9 and 4/13 for 10 cards after the first two or three cards in a hand).

My approach was to calculate the probability of all possible dealer totals as before, but using an enumeration of all unqiue dealer hands and their exact probabilities of being drawn from a full deck.
Those probabilities were then used to evaluate the expected winnings for each unique player hand independently drawn from a full deck.

Doing this we get the following result:

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.0946|0.1298|0.1758|0.2295|0.2366|0.1455|0.0556|-0.0404|-0.1731|-0.3658|

**Overall:** -0.0024

Which is satisfyingly close to Thorp's -0.21%.

For reference, these are the uqique hand counts (considering order of draw) that have to be evaluated:

**Dealer Face Up Card / Unique Hand Count**
|  |Dealer|Player|
|--|--|--|
|  2|16390| 4726|
|  3|10509| 4978|
|  4| 6359| 2774|
|  5| 3904| 2313|
|  6| 2255| 2142|
|  7| 1414|72231|
|  8|  852|52550|
|  9|  566|69657|
| 10|  288|71582|
|Ace| 5995|50837|

Trivial on a computer, but out of the question for manual calculation.

## Even More Accurate Calculations (ala Thorp Book)

[See ewcalc2.py for full details]

Finally, in his 1966 book[5], after doing a lot more computer analysis, Thorp states that the correct expected winnings value for Baldwin's strategy is +0.09%.
He doesn't provide any details on his methods of calculation, but he must have considered the interdependency between the dealer and player card probabilities.

My approach was to extend the unique dealer and player hand enumeration technique, but nest the evaluation to look at all unique possible games.
In this version of my code I ditched the calculation of dealer total probabilities and instead evaluated the result of each unique game's conclusion.
The only approximation in this version of my code is that the value of a split hand is taken to be twice one half of the split.

This runs quite a bit slower, but still completes in reasonable time on a modern laptop computer.

The result matches Thorp:

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.1011|0.1375|0.1832|0.2375|0.2423|0.1465|0.0546|-0.0438|-0.1715|-0.3617|

**Overall:** 0.0009


## Other Strategies

My Python code can also be used to calculate the expected winnings for other simple strategies such as Cublertson[2] and Mimic Dealer mentioned by Baldwin et al.

### Culbertson

* Split pairs marked with S for dealer face up card

**Pair / Dealer Face Up Card**
| |2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|A|S|S|S|S|S|S|S|S|S|S|

* Stand on totals marked with S (or greater) for dealer face up card

**Total / Dealer Face Up Card**
|Hard Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|16| | | | | |S|S|S|S|S|
|15| | | | | | | | | | |
|14|S|S|S|S|S| | | | | |

|Soft Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|18|S|S|S|S|S|S|S|S|S|S|

#### Baldwin-style Calculation (baldwinpaper.py)

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.0731|0.0981|0.1275|0.1621|0.1775|0.1246|0.0442|-0.0458|-0.1716|-0.3710|

**Overall:** -0.0228

#### More Exact Calculation (ewcalc2.py)

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.0727|0.1008|0.1329|0.1685|0.1782|0.1156|0.0334|-0.0563|-0.1760|-0.3734|

**Overall:** -0.0255

### Mimic Dealer

* Stand on totals marked with S (or greater) for dealer face up card

**Total / Dealer Face Up Card**
|Hard Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|17|S|S|S|S|S|S|S|S|S|S|

|Soft Total|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|--|
|17|S|S|S|S|S|S|S|S|S|S|

#### Baldwin-style Calculation (baldwinpaper.py)

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.0161|0.0304|0.0473|0.0707|0.0955|0.1231|0.0376|-0.0563|-0.1833|-0.3656|

**Overall:** -0.0565

#### More Exact Calculation (ewcalc2.py)

**Expected Winnings / Dealer Face Up Card**
|2|3|4|5|6|7|8|9|10|A|
|--|--|--|--|--|--|--|--|--|--|
|0.0156|0.0281|0.0446|0.0661|0.0912|0.1218|0.0362|-0.0579|-0.1799|-0.3651|

**Overall:** -0.0568


## References

[1] Roger R. Baldwin, Wilbert E. Cantey, Herbert Maisel, and James P. McDermott. The optimum strategy in blackjack. Journal of the American Statistical Association, 51(275):429–429, 1956.

[2] Culbertson, E., Morehead, A. H., and Mott-Smith, G., Culbertson's Card Games Complete. New York: The Greystone Press, 1952.

[3] Roger R. Baldwin, Wilbert E. Cantey, Herbert Maisel, and James P. McDermott. Playing Blackjack to Win: A New Strategy for the Game of 21, 1957

[4] E. O. Thorp, A favorable Strategy for Twenty-One, Proc. Natl. Acad. Sci., 47(1), 110-112, 1961.

[5] E. O. Thorp, Beat The Dealer, Random House, New York, NY, 1966

Copyright (c) 2025 Greg Whitehead

MIT License
