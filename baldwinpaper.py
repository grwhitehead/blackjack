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

#
# Python implementation of the calculations described by Roger Baldwin, Wilbert Cantey, Herbert maisel, and James McDermott
# in their 1956 paper[1] solving for the optimum strategy in blackjack. Quotes from the paper describing the calculations
# precede the matching sections of code.
#
# [1] Roger R. Baldwin, Wilbert E. Cantey, Herbert Maisel, and James P. McDermott. The optimum strategy in blackjack.
# Journal of the American Statistical Association, 51(275):429–429, 1956.
#

import sys
from optparse import OptionParser

import math


def main(argv):
    optparser = OptionParser("usage: %prog [options] strategy")
    optparser.add_option("-v", action="store_true", dest="verbose", default=False, help="verbose output")
    optparser.add_option("-e", action="store_true", dest="error", default=False, help="print error tables")
    (opts, args) = optparser.parse_args()

    if opts.verbose:
        print("verbose:",opts.verbose)
        print("args:",args)
    
    # Some notation will facilitate the description of the optimum strategy for drawing.
    #
    # Let D be the numerical value of the dealer's up card. D = 2, 3, * ,10, (1, 11).
    #
    # Let M = M((D) be an integer such that if the dealer's up card is D and player's total
    # is unique and less than M(D), the player should draw; while if the player's total
    # is unique and greater or equal to M(D), the player should stand. The ten integers
    # M(D) are known as the minimum standing numbers for unique hands. Let us define M*(D)
    # in the same way for soft hands with the understanding that "player's total" means
    # the larger of the two possible totals.
    #
    # Define X = X(D) as the set of values of x for which the player should double down
    # when the dealer's up card is D.
    #
    # Let Y = Y(D) denote the values of y for which a pair of y's should be split when the
    # dealer's up card is D.
        
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
        
    # probability of drawing a sequence of cards given a set of already dealt cards
    def drawProb(dealt, hand):
        p = 1.0
        for i in range(len(hand)):
            p = p*drawProb1(dealt+hand[0:i], hand[i])
        return p
    

    # III. EVALUATION OF THE DEALER'S PROBABILITIES, P(T=t).
    #
    # In the first stage an exact evaluation was made of P(T3=v), the probability
    # that the dealer obtains a total of v on his first three cards. These numbers,
    # known as "three-card probabilities," were computed separately for each
    # value of D, the dealer's first card. In cases where the rules required the
    # dealer to stand on two cards, the probabilities for the totals thus obtained
    # were included with the three-card probabilities.

    dealer3TotalProbs = [[[0 for t in range(23)] for a in range(2)] for dfu in cards]
    for dfu in cards:
        for d2 in cards:
            t,a = handTotal([dfu, d2])
            if t < 17:
                for d3 in cards:
                    t,a = handTotal([dfu, d2, d3])
                    p = drawProb([dfu], [d2, d3])
                    if t > 21:
                        dealer3TotalProbs[dfu-1][a][0] += p
                    else:
                        dealer3TotalProbs[dfu-1][a][t] += p
            else:
                p = drawProb([dfu], [d2])
                if t == 21:
                    dealer3TotalProbs[dfu-1][a][22] += p
                else:
                    dealer3TotalProbs[dfu-1][a][t] += p

    # In the second stage a table was developed which gives approximate values
    # for P(T=t/Tp=t,), the conditional probability that the dealer obtains a
    # final total t (t >= 17) given a partial total tp, (tp < 17). The table was
    # developed under the following simplifying assumptions: (1) the probability
    # of drawing any card in the deck is 1/52 ("equiprobability"); and (2) no
    # matter how many cards the player draws, the probability of receiving any
    # particular card on the next draw is still 1/52 ("sampling with replacement").

    dealerCTotalProbs = [[[[0 for t in range(23)] for t1 in range(22)] for a1 in [0,1]] for dfu in cards]
    def buildDTP2(dfu, t1, a1, t, a, p):
        if t > 21:
            dealerCTotalProbs[dfu-1][a1][t1][0] += p
        elif t >= 17:
            dealerCTotalProbs[dfu-1][a1][t1][t] += p
        else:
            for c in cards:
                pc = drawProb1([],c)
                tc = t+c
                ac = a
                if c == 1:
                    tc += 10
                    ac += 1
                while tc > 21 and ac > 0:
                    tc -= 10
                    ac -= 1
                buildDTP2(dfu, t1, a1, tc, ac, pc*p)
    def buildDTP(dfu, t1, a1):
        buildDTP2(dfu, t1, a1, t1, a1, 1.0)
    for dfu in cards:
        for a1 in range(2):
            for t1 in range((5 if a1 == 0 else 13),17):
                buildDTP(dfu, t1, a1)

    # In the third stage the results from the previous stages are combined yielding
    # the following approximation for P(T = t) for t >= 17.
    # P(T = t) = P(T3 = t) + sum for j<17 of P(T3 = j)P(T = t/Tp = j)

    dealerTotalProbs = [[0 for t in range(23)] for dfu in cards]
    for dfu in cards:
        dealerTotalProbs[dfu-1][0] = dealer3TotalProbs[dfu-1][0][0]
        for a1 in range(2):
            for t1 in range(22):
                dealerTotalProbs[dfu-1][0] += dealer3TotalProbs[dfu-1][a1][t1]*dealerCTotalProbs[dfu-1][a1][t1][0]
        for t in range(17,23):
            for a in range(2):
                dealerTotalProbs[dfu-1][t] += dealer3TotalProbs[dfu-1][a][t]
            for a1 in range(2):
                for t1 in range((5 if a1 == 0 else 13),17):
                    dealerTotalProbs[dfu-1][t] += dealer3TotalProbs[dfu-1][a1][t1]*dealerCTotalProbs[dfu-1][a1][t1][t]
    if opts.verbose:
        print("\ndealer total probabilities bust(0) 1 to 21 natural(22)")
        for dfu in cards:
            print(dfu,dealerTotalProbs[dfu-1])
        print("sums")
        for dfu in cards:
            print(dfu,sum(dealerTotalProbs[dfu-1]))

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
            print(dfu,sum(dealerTotalProbsNoNatural[dfu-1]))


    # IV. METHODS OF ANALYSIS FOR SPECIAL SITUATIONS
    #
    # The method of analysis for all special situations requires tables of P(H=h/Hp=hp),
    # the conditional probability the player obtains a final total of h { h >= M(D) }
    # given that he has a partial total of hp { hp(unique) < M(D), hp(soft) < M*(D) } and
    # draws or stands following M(D) and M*(D).
    #
    # The tables were worked out with the same assumptions of equiprobability and
    # sampling with replacement as in the corresponding tables of conditional probabilities
    # for the dealer.
    #
    # Separate tables were required for each of the following four cases:
    # D 2, 3 where M(D) = 13 and M*(D) = 18;
    # D = 4, 5, 6 where M(D) = 12 and M* (D) = 18;
    # D = 7, 8, (1, 11) where M(D) = 17 and M*(D) = 19;
    # and D = 9, 10 where M(D) = 17 and M*(D) = 19.

    playerCTotalProbs = [[[[0 for tm in range(22)] for th in range(22)] for ah in [0,1]] for dfu in cards]
    def buildPTP2(dfu, th, ah, t, a, p):
        if t > 21:
            playerCTotalProbs[dfu-1][ah][th][0] += p
        elif t >= M_D(dfu, a):
            playerCTotalProbs[dfu-1][ah][th][t] += p
        else:
            for c in cards:
                pc = drawProb1([], c)
                tc = t+c
                ac = a
                if c == 1:
                    tc += 10
                    ac += 1
                while tc > 21 and ac > 0:
                    tc -= 10
                    ac -= 1
                buildPTP2(dfu, th, ah, tc, ac, pc*p)
    def buildPTP(dfu, th, ah):
        buildPTP2(dfu, th, ah, th, ah, 1.0)
    for dfu in cards:
        for ah in range(2):
            for th in range((5 if ah == 0 else 13),22):
                buildPTP(dfu, th, ah)
    if opts.verbose:
        print("\nplayer conditional total probabilities bust(0) 1 to 21")
        for dfu in cards:
            for ah in range(2):
                for th in range((5 if ah == 0 else 13),22):
                    print(dfu,ah,th,playerCTotalProbs[dfu-1][ah][th])
        print("sums")
        for dfu in cards:
            for ah in range(2):
                for th in range((5 if ah == 0 else 13),22):
                    print(dfu,ah,th,sum(playerCTotalProbs[dfu-1][ah][th]))


    # V. THE PLAYER'S MATHEMATICAL EXPECTATION
    #
    # The mathematical expectation of the player is given by
    #
    # E(W) = 1/13 sum for D<>10 of E(WD) + 4/13 sum for D=10 of E(W10)
    #
    # where WD is the amount won by the player on a single hand when the dealer's up card is D.
    # When D = 10 and (1, 11) one must calculate E(WD) under two conditions: (1) given the dealer
    # does not obtain a natural, and (2) given that he does. These conditional expectations are
    # then multiplied by the probabilities for events (1) and (2) to obtain E(WD).
    #
    # The first step in obtaining E(WD) is to calculate the probabilities for the various hands
    # formed by the player's two hole cards. It is assumed that the hole cards are drawn from a
    # deck which is complete except for one D-counting card.
    #
    # In the case where D = 10 or (1, 11) and the dealer has a natural
    # E(WD) = - 1 [1 - P(the hole cards form a natural)].
    #
    # In all other cases E(WD) is the sum of the following four terms:
    # (1) 3/2 P(the hole cards form a natural),
    # (2) sum for y in Y(D) of P(the hole cards are a pair of y's) Esplit;y
    # (3) sum for j in X(D) of P(the hole cards total j) 2 Ed;j
    # (4) sum for j not in X(D) of P(the hole cards total j) EM,M*;j
    #
    # In the last two sums it is understood that the hole cards do not form a natural or a
    # pair of y's with y in Y(D).

    probPlayerNatural = [0 for dfu in cards]
    for dfu in cards:
        probPlayerNatural[dfu-1] = drawProb([dfu], [1, 10]) + drawProb([dfu], [10, 1])
    if opts.verbose:
        print("\nprobability player hole cards form a natural")
        for dfu in cards:
            print(dfu,probPlayerNatural[dfu-1])

    probPlayerPair = [[0 for c in cards] for dfu in cards]
    for dfu in cards:
        for c in cards:
            probPlayerPair[dfu-1][c-1] = drawProb([dfu], [c, c])
    if opts.verbose:
        print("\nprobability player hole cards form a pair")
        for dfu in cards:
            print(dfu,probPlayerPair[dfu-1])

    probPlayerHoleNoNaturalNoPair = [[[0 for t in range(22)] for a in [0,1]] for dfu in cards]
    for dfu in cards:
        for i in cards:
            for j in cards:
                if i == j: # skip pairs
                    continue
                t,a = handTotal([i,j])
                if t == 21: # skip naturals
                    continue
                probPlayerHoleNoNaturalNoPair[dfu-1][a][t] += drawProb([dfu], [i,j])
    if opts.verbose:
        print("\nprobability player hole cards total j (and aren't natural or pair)")
        for dfu in cards:
            #print(dfu, probPlayerHoleNoNaturalNoPair[dfu-1])
            print(dfu,
                  sum(probPlayerHoleNoNaturalNoPair[dfu-1][0]), # hard totals
                  sum(probPlayerHoleNoNaturalNoPair[dfu-1][1]), # soft totals
                  probPlayerNatural[dfu-1], # naturals
                  sum(probPlayerPair[dfu-1]), # pairs
                  sum(probPlayerHoleNoNaturalNoPair[dfu-1][0])+sum(probPlayerHoleNoNaturalNoPair[dfu-1][1])+probPlayerNatural[dfu-1]+sum(probPlayerPair[dfu-1])) # total

    # Standing
    #
    # Let us define T, a random variable, as the final total obtained by the dealer.
    # If T > 21 or if T < x, the player standing on x wins the bet, assumed here to be
    # one unit. If T = x, no money changes hands, while if x < T < 21, the player loses
    # one unit. Consequently,
    #
    # Es,x = P(T > 21) + P(T < x) - P(x < T < 21) for x <= 21
    # Es,x = -1 for x > 21
    #
    def ew_s(dfu, t, a):
        # player loses on bust
        if t > 21:
            return -1
        # player wins on dealer bust
        ew = dealerTotalProbsNoNatural[dfu-1][0]
        # player wins on dealer total less than t
        for i in range(17,t):
            ew += dealerTotalProbsNoNatural[dfu-1][i]
        # player loses on dealer total greater than t (and not bust)
        for i in range(t+1,22):
            ew -= dealerTotalProbsNoNatural[dfu-1][i]
        return ew

    # Drawing one card
    #
    # In discussing Ed,x one must define a second random variable, J, as the total obtained
    # by the player upon drawing one card. In cases where this total can take on two values
    # not exceeding 21, J represents the larger total.
    #
    # T >= 17, so if J < 17, the player wins when T > 21 and loses for all other values of T.
    # His mathematical expectation in this situation is
    # P(T > 21) - [1 - P(T > 21)] = 2P(T > 21) - 1.
    #
    # If 17 <= J <= 21, the player's mathematical expectation is
    # P(T > 21) + P(T < J) - P(J < T < 21).
    #
    # If J > 21, the player's mathematical expectation is -1.
    #
    # The value of J affects T only through eliminating the possibility that the dealer draws
    # one particular card of value J-x. Consequently, little error is introduced in making the
    # assumption that J and T are independent and writing
    #
    # Ed,x = P(J < 17) [2P(T > 21) - 1] - P(J > 21)
    #        + sum for j = 17 to 21 of P(J = j) [P(T > 21) + P(T < j) - P(j < T <= 21)].
    #
    def ew_d(dfu, t, a):
        ew = 0.0
        for c in cards:
            pc = drawProb1([], c)
            tc = t+c
            ac = a
            if c == 1:
                tc += 10
                ac += 1
            while tc > 21 and ac > 0:
                tc -= 10
                ac -= 1
                
            if tc < 17:
                # player wins on dealer bust, loses otherwise (dealer's total is always >= 17)
                ew += pc*(2*dealerTotalProbsNoNatural[dfu-1][0] - 1)
            elif tc > 21:
                # player loses on bust
                ew -= pc
            else:
                # player wins on dealer bust
                ew += pc*dealerTotalProbsNoNatural[dfu-1][0]
                # player wins on dealer total less than t
                for i in range(17,tc):
                    ew += pc*dealerTotalProbsNoNatural[dfu-1][i]
                # player loses on dealer total greater than t (and not bust)
                for i in range(tc+1,22):
                    ew -= pc*dealerTotalProbsNoNatural[dfu-1][i]
           
        return ew

    # Drawing to M,M*
    #
    # EM,M*;x = Es,x for x(unique) >= M or x(soft) >= M*
    #           sum for h >= M of P(H = h/Hp = x) Es,h otherwise.
    #
    def ew_m(dfu, t, a):
        m = M_D(dfu,a)
        if t >= m:
            return ew_s(dfu, t, a)
        ew = 0.0
        for h in range(m,22):
            ew += playerCTotalProbs[dfu-1][a][t][h]*ew_s(dfu, h, 0) # stand at h >= M
        ew -= playerCTotalProbs[dfu-1][a][t][0] # bust
        return ew

    # Splitting
    #
    # In the case of splitting a pair of y's a separate analysis is required for every
    # combination of y and D. The results for doubling down must be used inasmuch as a
    # player may split a pair and subsequently double down
    #
    # 1/2 Esplit,y = sum for j in X of P(J = j)2Ed,j
    #                sum for j not in x of P(J = j)EM,M*;j
    #
    # In the special case where y = (1, 11), the player splitting is allowed to draw only
    # one more card and cannot double down. Thus
    #
    # 1/2 Esplit,(1,11) = sum for all j of P(J = j)Es,j
    #
    def ew_split(dfu, y):
        ew = 0.0
        for c in cards:
            pc = drawProb1([dfu, y, y], c)
            tc,ac = handTotal([y, c])
            if y == 1:
                ew += pc*ew_s(dfu, tc, ac)
            elif tc in X_D(dfu, ac):
                ew += pc*2*ew_d(dfu, tc, ac)
            else:
                ew += pc*ew_m(dfu, tc, ac)
        return 2*ew


    def ewDealerNatural_D(dfu):
        return -(1.0-probPlayerNatural[dfu-1])

    def ewDealerNoNatural_D(dfu):
        ew = 1.5*probPlayerNatural[dfu-1]
        for c in cards:
            if c in Y_D(dfu):
                ew += probPlayerPair[dfu-1][c-1]*ew_split(dfu, c)
            else:
                t,a = handTotal([c,c])
                if t in X_D(dfu, a):
                    ew += probPlayerPair[dfu-1][c-1]*2*ew_d(dfu, t, a)
                else:
                    ew += probPlayerPair[dfu-1][c-1]*ew_m(dfu, t, a)
        for j in range(1,22):
            if j in X_D(dfu, 0):
                ew += probPlayerHoleNoNaturalNoPair[dfu-1][0][j]*2*ew_d(dfu, j, 0)
            else:
                ew += probPlayerHoleNoNaturalNoPair[dfu-1][0][j]*ew_m(dfu, j, 0)
            if j in X_D(dfu, 1):
                ew += probPlayerHoleNoNaturalNoPair[dfu-1][1][j]*2*ew_d(dfu, j, 1)
            else:
                ew += probPlayerHoleNoNaturalNoPair[dfu-1][1][j]*ew_m(dfu, j, 1)
        return ew

    def ew_D(dfu):
        ew = dealerTotalProbs[dfu-1][22]*ewDealerNatural_D(dfu)
        ew += (1.0-dealerTotalProbs[dfu-1][22])*ewDealerNoNatural_D(dfu)
        return ew

    expectedWinnings = [0 for dfu in cards]
    ew = 0.0
    for dfu in cards:
        expectedWinnings[dfu-1] = ew_D(dfu)
        ew += expectedWinnings[dfu-1]*deckCounts[dfu-1]/deckCountTotal
    
    print("expected winnings")
    for dfu in cards:
        print(dfu,expectedWinnings[dfu-1])
    print("overall expected winnings")
    print(ew)

    if opts.error:
        print("\ndealer total probabilities ERR")
        dealerTotalProbs_paper = [
            # 17        18        19        20        21      natural  bust
            [0.141781, 0.134885, 0.131432, 0.123829, 0.119581, 0.0, 0.348492],      # 2
            [0.133533, 0.133052, 0.126197, 0.122563, 0.114903, 0.0, 0.369751],      # 3
            [0.132206, 0.116037, 0.122553, 0.117930, 0.114292, 0.0, 0.396983],      # 4
            [0.121374, 0.124511, 0.117753, 0.105446, 0.107823, 0.0, 0.423092],      # 5
            [0.167625, 0.107233, 0.108018, 0.101260, 0.098364, 0.0, 0.417499],      # 6
            [0.372743, 0.139017, 0.077841, 0.079409, 0.073437, 0.0, 0.257552],      # 7
            [0.131202, 0.363359, 0.129634, 0.068457, 0.070026, 0.0, 0.237322],      # 8
            [0.122256, 0.104217, 0.357550, 0.122256, 0.061079, 0.0, 0.232643],      # 9
            [0.114756, 0.113186, 0.114756, 0.328873, 0.036324, 0.078431, 0.213674],  # 10
            [0.128147, 0.131284, 0.129716, 0.131284, 0.051284, 0.313725, 0.114560], # Ace
        ]
        dealerTotalProbs_paper_cols = [17, 18, 19, 20, 21, 22, 0]
        dealerTotalProbs_paper_rows = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
        cumerrsq = 0.0
        dealerTotalProbs_err = [[0 for t in dealerTotalProbs_paper_cols] for dfu in dealerTotalProbs_paper_rows]
        print(dealerTotalProbs_paper_cols)
        for i in range(len(dealerTotalProbs_paper_rows)):
            for j in range(len(dealerTotalProbs_paper_cols)):
                dealerTotalProbs_err[i][j] = round(dealerTotalProbs[dealerTotalProbs_paper_rows[i]-1][dealerTotalProbs_paper_cols[j]], 6) - dealerTotalProbs_paper[i][j]
                cumerrsq = dealerTotalProbs_err[i][j]**2
            print(dealerTotalProbs_paper_rows[i], dealerTotalProbs_err[i])
        print("cumerrsq",cumerrsq)

        print("\ndealer total probabilities NO NATURAL ERR")
        dealerTotalProbsNoNatural_paper = [
            # 17       18       19       20       21       natural  bust
            [.124522, .122819, .124522, .356862, .039415, .000000, .231859], # 10
            [.186728, .191299, .189015, .191299, .074728, .000000, .166930], # Ace
        ]
        dealerTotalProbsNoNatural_paper_cols = [17, 18, 19, 20, 21, 22, 0]
        dealerTotalProbsNoNatural_paper_rows = [10, 1]
        dealerTotalProbsNoNatural_err = [[0 for t in dealerTotalProbsNoNatural_paper_cols] for dfu in dealerTotalProbsNoNatural_paper_rows]
        print(dealerTotalProbsNoNatural_paper_cols)
        for i in range(len(dealerTotalProbsNoNatural_paper_rows)):
            for j in range(len(dealerTotalProbsNoNatural_paper_cols)):
                dealerTotalProbsNoNatural_err[i][j] = round(dealerTotalProbsNoNatural[dealerTotalProbsNoNatural_paper_rows[i]-1][dealerTotalProbsNoNatural_paper_cols[j]], 6) - dealerTotalProbsNoNatural_paper[i][j]
                cumerrsq = dealerTotalProbsNoNatural_err[i][j]**2
            print(dealerTotalProbsNoNatural_paper_rows[i], dealerTotalProbsNoNatural_err[i])
        print("cumerrsq",cumerrsq)

        print("\nexpected winnings ERR")
        expectedWinnings_paper = [0.090, 0.123, 0.167, 0.218, 0.230, 0.148, 0.056, -0.043, -0.176, -0.363]
        expectedWinnings_paper_cols = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
        expectedWinnings_err = [0 for dfu in expectedWinnings_paper_cols]
        for i in range(len(expectedWinnings_paper_cols)):
            expectedWinnings_err[i] = round(expectedWinnings[expectedWinnings_paper_cols[i]-1], 3) - expectedWinnings_paper[i]
            print(expectedWinnings_paper_cols[i], expectedWinnings_err[i])
            
        print("\noverall expected winnings ERR")
        ew_paper = -0.006
        ew_err = ew-ew_paper
        print(ew_err)
        
        def cardStr(c):
            return 'A' if c == 1 else str(c)
        
        def printDTPTable(dtp, rows, cols, domap):
            h = "| |"
            h2 = "|--|"
            for j in range(len(cols)-2):
                h += f"{cols[j]}|"
                h2 += "--|"
            h += "Natural|Bust|"
            h2 += "--|--|"
            print(h)
            print(h2)
            for i in range(len(rows)):
                r = "|"+cardStr(rows[i])+"|"
                for j in range(len(cols)):
                    if domap:
                        r += f"{dtp[rows[i]-1][cols[j]]:.6f}|"
                    else:
                        r += f"{dtp[i][j]:.6f}|"
                print(r)
        print("\nDealer Total Probabilities (calculated)")
        print("Dealer Face Up Card / Dealer Total")
        printDTPTable(dealerTotalProbs, dealerTotalProbs_paper_rows, dealerTotalProbs_paper_cols, True)
        print("\nDealer Total Probabilities (paper)")
        print("Dealer Face Up Card / Dealer Total")
        printDTPTable(dealerTotalProbs_paper, dealerTotalProbs_paper_rows, dealerTotalProbs_paper_cols, False)
        print("\nDealer Total Probabilities (error)")
        print("Dealer Face Up Card / Dealer Total")
        printDTPTable(dealerTotalProbs_err, dealerTotalProbs_paper_rows, dealerTotalProbs_paper_cols, False)

        print("\nDealer Total Probabilities NO NATURAL (calculated)")
        print("Dealer Face Up Card / Dealer Total")
        printDTPTable(dealerTotalProbsNoNatural, dealerTotalProbsNoNatural_paper_rows, dealerTotalProbsNoNatural_paper_cols, True)
        print("\nDealer Total Probabilities NO NATURAL (paper)")
        print("Dealer Face Up Card / Dealer Total")
        printDTPTable(dealerTotalProbsNoNatural_paper, dealerTotalProbsNoNatural_paper_rows, dealerTotalProbsNoNatural_paper_cols, False)
        print("\nDealer Total Probabilities NO NATURAL (error)")
        print("Dealer Face Up Card / Dealer Total")
        printDTPTable(dealerTotalProbsNoNatural_err, dealerTotalProbsNoNatural_paper_rows, dealerTotalProbsNoNatural_paper_cols, False)

        def printEWTable(ews, cols, domap):
            h = "|"
            h2 = "|"
            for i in range(len(cols)):
                h += cardStr(cols[i])+"|"
                h2 += "--|"
            print(h)
            print(h2)
            r = "|"
            for i in range(len(cols)):
                if domap:
                    r += f"{ews[cols[i]-1]:.3f}|"
                else:
                    r += f"{ews[i]:.3f}|"
            print(r)
        print("\nExpected Winnings (calculated)")
        print("Dealer Face Up Card")
        printEWTable(expectedWinnings, expectedWinnings_paper_cols, True)
        print(f"Overall {ew:.3f}")
        print("\nExpected Winnings (paper)")
        print("Dealer Face Up Card")
        printEWTable(expectedWinnings_paper, expectedWinnings_paper_cols, False)
        print(f"Overall {ew_paper:.3f}")
        print("\nExpected Winnings (error)")
        print("Dealer Face Up Card")
        printEWTable(expectedWinnings_err, expectedWinnings_paper_cols, False)
        print(f"Overall {ew_err:.3f}")

if __name__ == '__main__':
    main(sys.argv)
