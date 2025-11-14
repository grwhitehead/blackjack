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
    optparser.add_option("-d", "--dfu", action="store", type="int", dest="dfu", default=0, help="dealer face up card to analyze (default all)")
    (opts, args) = optparser.parse_args()

    if opts.verbose:
        print("verbose:",opts.verbose)
        print("dfu:",opts.dfu)
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
        nc = deckCounts[c-1] - cardCount(dealt, c)
        if nc > 0:
            return nc/(deckCountTotal-len(dealt))
        return 0
        
    # probability of drawing a hand given a set of already dealt cards
    def drawProb(dealt, hand):
        p = 1.0
        for i in range(len(hand)):
            p = p*drawProb1(dealt+hand[0:i], hand[i])
        return p

    
    dfus = cards
    if opts.dfu:
        dfus = [opts.dfu]


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
    

    def cardsRemaining(dfu, d2, s, h, k):
        return cardCount(h, k) < deckCounts[k-1] - (1 if dfu == k else 0) - (1 if d2 == k else 0) - (1 if s == k else 0)

    # expand player partial hand using basic strategy
    def expandPlayerHand(dfu, d2, s, b, h):
        t,a = handTotal(h)
        # splitting
        if s == 0 and len(h) == 2 and h[0] == h[1]:
            if h[0] in Y_D(dfu):
                if h[0] == 1:
                    xh = []
                    for k in cards:
                        if cardsRemaining(dfu, d2, s, h, k):
                            xh += [[h[0], b, h[0:1] + [k]]]
                    return xh
                else:
                    xh = []
                    for k in cards:
                        if cardsRemaining(dfu, d2, s, h, k):
                            xh += expandPlayerHand(dfu, d2, h[0], b, h[0:1] + [k])
                    return xh
        # doubling
        if len(h) == 2:
            if t in X_D(dfu, a):
                xh = []
                for k in cards:
                    if cardsRemaining(dfu, d2, s, h, k):
                        xh += [[s, b*2, h + [k]]]
                return xh
        # hitting
        if t < M_D(dfu, a):
            xh = []
            for k in cards:
                if cardsRemaining(dfu, d2, s, h, k):
                    xh += expandPlayerHand(dfu, d2, s, b, h + [k])
            return xh
        return [[s, b, h]]


    # compute expected winnings
    print("expected winnings by dealer face up card")
    expectedWinnings = [0.0 for dfu in cards]
    overallExpectedWinnings = 0.0
    for dfu in dfus:
        ptotal = 0
        for d2 in cards:
            dnat = handTotal([dfu, d2])[0] == 21
            dhs = expandDealerHand([dfu, d2])
            # initial player hands [a,b] and [b,a] are equivalent, so only analyze for b <= a and double results for b < a
            for p1i in range(len(cards)):
                p1 = cards[p1i]
                for p2i in range(p1i+1):
                    p2 = cards[p2i]
                    pnat = handTotal([p1, p2])[0] == 21
                    if dnat:
                        # dealer has a natural
                        if not pnat:
                            # player loses b if they don't also have a natural
                            w = -b
                            p = drawProb([dfu], [d2, p1, p2])*(2 if p2 < p1 else 1)
                            expectedWinnings[dfu-1] += p*w
                            ptotal += p
                        else:
                            p = drawProb([dfu], [d2, p1, p2])*(2 if p2 < p1 else 1)
                            ptotal += p
                        continue
                    if pnat:
                        # player wins 1.5*b on a natural
                        w = 1.5*b
                        p = drawProb([dfu], [d2, p1, p2])*(2 if p2 < p1 else 1)
                        expectedWinnings[dfu-1] += p*w
                        ptotal += p
                        continue
                    # no naturals
                    phs = expandPlayerHand(dfu, d2, 0, 1, [p1, p2])
                    for phi in range(len(phs)):
                        s,b,h = phs[phi]
                        t,a = handTotal(h)
                        if t > 21:
                            # player loses b on bust
                            w = -b
                            p = drawProb([dfu], dh[1:2] + ([s] if s > 0 else []) + h)*(2 if p2 < p1 else 1)
                            expectedWinnings[dfu-1] += p*w*(2 if s > 0 else 1)
                            ptotal += p 
                            continue
                        for dhi in range(len(dhs)):
                            dh = dhs[dhi]
                            dt,da = handTotal(dh)
                            p = drawProb([dfu], dh[1:2] + ([s] if s > 0 else []) + h + dh[2:])*(2 if p2 < p1 else 1)
                            if p == 0:
                                # skip impossible hand combinations
                                continue
                            w = 0
                            if dt > 21:
                                # player wins b if dealer busts
                                w = b
                            elif dt < t:
                                # player wins b if dealer total is less than t
                                w = b
                            elif dt > t:
                                # player loses b if dealer total is greater than t
                                w = -b
                            expectedWinnings[dfu-1] += p*w*(2 if s > 0 else 1)
                            ptotal += p
        if opts.verbose:
            print(dfu, expectedWinnings[dfu-1], ptotal)
        else:
            print(dfu, expectedWinnings[dfu-1])
        overallExpectedWinnings += expectedWinnings[dfu-1]*deckCounts[dfu-1]/deckCountTotal
    if not opts.dfu:
        print("overall expected winnings")
        print(overallExpectedWinnings)

if __name__ == '__main__':
    main(sys.argv)
