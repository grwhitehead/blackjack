#!/usr/bin/env python3
#coding: utf-8

#
# MIT License
#
# Copyright (c) 2025 Greg Whitehead
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
from optparse import OptionParser

import math


def main(argv):
    optparser = OptionParser("usage: %prog [options] strategy")
    optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
    (opts, args) = optparser.parse_args()

    if opts.verbose:
        print("verbose:",opts.verbose)
        print("args:",args)
        
    strategy = "baldwin-optimum"
    if len(args) > 0:
        strategy = args.pop()
    print("Using strategy:",strategy)

    if strategy == "baldwin-optimum":
        def M_D(dfu, a):
            if a == 0:
                # hard
                if dfu >= 2 and dfu <= 3:
                    return 13
                if dfu >= 4 and dfu <= 6:
                    return 12
                if True: # dfu >= 7 or dfu == 1
                    return 17
            else:
                # soft
                if dfu >= 1 and dfu <= 8:
                    return 18
                if True: # dfu >= 9 and dfu <= 10
                    return 19
        def X_D(dfu, a):
            x = []
            if a == 0:
                # hard
                if dfu >= 2 and dfu <= 10:
                    x += [11]
                if dfu >= 2 and dfu <= 9:
                    x += [10]
                if dfu >= 2 and dfu <= 6:
                    x += [9]
            else:
                # soft
                if dfu >= 4 and dfu <= 6:
                    x += [18]
                if dfu >= 3 and dfu <= 6:
                    x += [17]
                if dfu >= 5 and dfu <= 6:
                    x += [13,14,15,16]
                if dfu == 5:
                    x += [12]
            return x
        def Y_D (dfu):
            y = [1,8]
            if (dfu >= 2 and dfu <= 6) or dfu == 8 or dfu == 9:
                y += [9]
            if dfu >= 2 and dfu <= 8:
                y += [7]
            if dfu >= 2 and dfu <= 7:
                y += [2,3,6]
            if dfu == 5:
                y += [4]
            return y

    elif strategy == "culbertson":
        def M_D(dfu, a):
            if a == 0:
                if dfu >= 2 and dfu <= 6:
                    return 14
                if True: # dfu >= 7 or dfu == 1:
                    return 16
            else:
                return 18
        def X_D(dfu, a):
            return []
        def Y_D (dfu):
            return [1]

    elif strategy == "mimicdealer":
        # mimic dealer
        def M_D(dfu, a):
            return 17
        def X_D(dfu, a):
            return []
        def Y_D (dfu):
            return []
        
    else:
        raise Exception("unknown strategy")

    
    # utility functions
    
    cards =      [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    deckCounts = [4, 4, 4, 4, 4, 4, 4, 4, 4, 16]
    deckCountTotal = sum(deckCounts)

    # number of times card c appears in hand h
    def cardCount(hand, c):
        n = 0
        for k in hand:
            if k == c:
                n += 1
        return n

    # hand total t,a (total is soft if a > 0)
    def handTotal(hand):
        t = 0
        a = 0
        for c in hand:
            t += c
            if c == 1:
                a = 1
        if a and t < 12:
            t += 10
        else:
            a = 0
        return t,a

    # probability of drawing a card given a set of already dealt cards
    def drawProb1(dealt, c):
        return (deckCounts[c-1]-cardCount(dealt,c))/(deckCountTotal-len(dealt))
        
    # probability of drawing a hand given a set of already dealt cards
    def drawProb(dealt, hand):
        p = 1.0
        for i in range(len(hand)):
            p = p*drawProb1(dealt+hand[0:i], hand[i])
        return p

    # expand dealer partial hand
    def expandDealerHand(h):
        t,a = handTotal(h)
        if t < 17:
            xh = []
            for k in cards:
                if cardCount(h, k) < deckCounts[k-1]:
                    xh += expandDealerHand(h + [k])
            return xh
        return [h]

    # all unique dealer hands
    dealerHands = [[] for dfu in cards]
    for dfu in cards:
        for c in cards:
            dealerHands[dfu-1] += expandDealerHand([dfu, c])
    if opts.verbose:
        print("\nunique dealer hands")
        for dfu in cards:
            print(dfu, len(dealerHands[dfu-1]))
        print("total dealer hand prob")
        for dfu in cards:
            p = 0.0
            for h in  dealerHands[dfu-1]:
                p += drawProb([dfu], h[1:])
            print(dfu,p)

    # probabilities of dealer totals by face up card (busts are stored in 0, naturals are stored in 22)
    dealerTotalProbs = [[0 for t in range(23)] for dfu in cards]
    for dfu in cards:
        for h in dealerHands[dfu-1]:
            t,a = handTotal(h) # hand total
            p = drawProb([dfu], h[1:])
            if t > 21:
                dealerTotalProbs[dfu-1][0] += p # bust
            elif len(h) == 2 and t == 21:
                dealerTotalProbs[dfu-1][22] += p # natural
            else:
                dealerTotalProbs[dfu-1][t] += p # total
    if opts.verbose:
        print("\ndealer total probabilities bust(0) 1 to 21 natural(22)")
        for dfu in cards:
            print(dfu, dealerTotalProbs[dfu-1])
        print("sums")
        for dfu in cards:
            print(dfu, sum(dealerTotalProbs[dfu-1]))

    dealerTotalProbsNoNatural = [[0 for t in range(23)] for dfu in cards]
    for dfu in cards:
        for t in range(22):
            dealerTotalProbsNoNatural[dfu-1][t] = dealerTotalProbs[dfu-1][t]/(1-dealerTotalProbs[dfu-1][22])
    if opts.verbose:
        print("\ndealer total probabilities bust(0) 1 to 21 natural(22) NO NATURAL")
        for dfu in cards:
            print(dfu, dealerTotalProbsNoNatural[dfu-1])
        print("sums")
        for dfu in cards:
            print(dfu, sum(dealerTotalProbsNoNatural[dfu-1]))

    def probDealerNatural(dfu):
        return dealerTotalProbs[dfu-1][22]

    def probDealerNoNatural(dfu):
        return 1.0-dealerTotalProbs[dfu-1][22]

    def probDealerNoNaturalBust(dfu):
        return dealerTotalProbsNoNatural[dfu-1][0]

    def probDealerNoNaturalTotalLessThan(dfu, t):
        p = 0.0
        for i in range(17,t):
            p += dealerTotalProbsNoNatural[dfu-1][i]
        return p

    def probDealerNoNaturalTotalGreaterThan(dfu, t):
        p = 0.0
        for i in range(t+1,22):
            p += dealerTotalProbsNoNatural[dfu-1][i]
        return p

    def cardsRemaining(dfu, s, h, k):
        return cardCount(h, k) < deckCounts[k-1] - (1 if dfu == k else 0) - (1 if s == k else 0)

    # expand player partial hand using basic strategy
    def expandPlayerHand(dfu, s, b, h):
        t,a = handTotal(h)
        # splitting
        if s == 0 and len(h) == 2 and h[0] == h[1]:
            if h[0] in Y_D(dfu):
                if h[0] == 1:
                    xh = []
                    for k in cards:
                        if cardsRemaining(dfu, s, h, k):
                            xh += [[h[0], b, h[0:1] + [k]]]
                    return xh
                else:
                    xh = []
                    for k in cards:
                        if cardsRemaining(dfu, s, h, k):
                            xh += expandPlayerHand(dfu, h[0], b, h[0:1] + [k])
                    return xh
        # doubling
        if len(h) == 2:
            if t in X_D(dfu, a):
                xh = []
                for k in cards:
                    if cardsRemaining(dfu, s, h, k):
                        xh += [[s, b*2, h + [k]]]
                return xh
        # hitting
        if t < M_D(dfu, a):
            xh = []
            for k in cards:
                if cardsRemaining(dfu, s, h, k):
                    xh += expandPlayerHand(dfu, s, b, h + [k])
            return xh
        return [[s, b, h]]

    # all unique player hands w/bets by dealer face up card
    playerHands = [[] for dfu in cards]
    for dfu in cards:
        for i in cards:
            for j in cards:
                playerHands[dfu-1] += expandPlayerHand(dfu, 0, 1, [i, j])
    if opts.verbose:
        print("\nunique player hands")
        for dfu in cards:
            print(dfu, len(playerHands[dfu-1]))
        print("total player hand prob")
        for dfu in cards:
            p = 0.0
            for s,b,h in playerHands[dfu-1]:
                if  s == 0:
                    p += drawProb([dfu], h)
                else:
                    p += drawProb([dfu], [s, s])*drawProb([dfu, s, s], h[1:])
            print(dfu,p)

    # compute expected winnings
    print("expected winnings by dealer face up card")
    expectedWinnings = [0.0 for dfu in cards]
    overallExpectedWinnings = 0.0
    for dfu in cards:
        for i in range(len(playerHands[dfu-1])):
            s,b,h = playerHands[dfu-1][i]
            t,a = handTotal(h)
            p = drawProb([dfu], ([s] if s > 0 else []) + h)
            w = 0.0
            if t > 21:
                # player loses b on bust
                w -= b
            elif t < 17:
                # player wins b on dealer bust
                w += b*probDealerNoNatural(dfu)*probDealerNoNaturalBust(dfu)
                # player loses b on all other possible dealer totals (dealer stands on 17)
                w -= b*probDealerNoNatural(dfu)*(1.0-probDealerNoNaturalBust(dfu))
            elif s == 0 and len(h) == 2 and t == 21:
                # player wins 1.5*b on a natural if dealer doesn't have a natural
                w += 1.5*b*probDealerNoNatural(dfu)
            else:
                # player loses b if dealer has a natural
                w -= b*probDealerNatural(dfu)
                # player wins b if dealer doesn't have a natural and dealer busts
                w += b*probDealerNoNatural(dfu)*probDealerNoNaturalBust(dfu)
                # player wins b if dealer doesn't have a natural and dealer total is less than t
                w += b*probDealerNoNatural(dfu)*probDealerNoNaturalTotalLessThan(dfu,t)
                # player loses b if dealer doesn't have a natural and dealer total is greater than t
                w -= b*probDealerNoNatural(dfu)*probDealerNoNaturalTotalGreaterThan(dfu,t)
            expectedWinnings[dfu-1] += p*w*(2 if s > 0 else 1)
        print(dfu, expectedWinnings[dfu-1])
        overallExpectedWinnings += expectedWinnings[dfu-1]*deckCounts[dfu-1]/deckCountTotal
    print("overall expected winnings")
    print(overallExpectedWinnings)

if __name__ == '__main__':
    main(sys.argv)
