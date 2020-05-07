from models import Card


def flush(cards):
    suits = [card.suit for card in cards]
    if len(set(suits)) == 1:
        hc = 0
        for card in cards:
            if card.number > hc:
                hc = card.number
        return hc

    return False


def straight(cards):
    number = [card.number for card in cards]
    number.sort()
    if not len(set(number)) == 5:
        return False
    if number[4] == 14 and number[3] == 5 and number[2] == 4 and number[1] == 3 and number[0] == 2:
        return 5
    else:
        if not number[0] + 1 == number[1]:
            return False
        if not number[1] + 1 == number[2]:
            return False
        if not number[2] + 1 == number[3]:
            return False
        if not number[3] + 1 == number[4]:
            return False
    return number[4]


def fourKind(cards):
    number = [card.number for card in cards]
    for value in number:
        if number.count(value) == 4:
            return value
    return False


def threeKind(cards):
    triple = []
    number = [card.number for card in cards]
    for value in number:
        if number.count(value) == 3:
            return value
    return False


def pairs(cards):
    pairs = []
    number = [card.number for card in cards]
    for value in number:
        if number.count(value) == 2 and value not in pairs:
            pairs.append(value)
    return pairs


def twoPairs(cards):
    pair = pairs(cards)
    if pair.count() == 2:
        return max(pair[0].number, pair[1].number)
    else:
        return False


def onePair(cards):
    pair = pairs(cards)
    if pair.count() == 1:
        return max(pair[0].number)
    else:
        return False


def highcard(cards):
    # [card.number for card in cards]
    highcard = None
    for card in cards:
        if highcard is None:
            highcard = card
        elif highcard.number < card.number:
            highcard = card
    return highcard


def pokerScore(cards):
    is_straight = straight(cards)
    is_flush = flush(cards)
    is_one_pair = onePair(cards)
    is_two_pairs = twoPairs(cards)
    is_three_kind = threeKind(cards)
    is_fourKind = fourKind(cards)

    # Royal flush
    if is_straight and is_flush and is_straight == 14:
        print("Royal Flush!!!")
        return 10
    # Straight flush
    elif is_straight and is_flush:
        print("Straight Flush!")
        return 9 + is_straight / 100.0
    # 4 of a kind
    elif is_fourKind:
        print("Four of a kind!")
        return 8 + is_fourKind / 100.0
    # Full House
    elif is_three_kind and is_one_pair:
        print("Full House!")
        return 7 + is_three_kind / 100.0
        # Flush
    elif is_flush:
        print("Flush!")
        return 6 + is_flush / 100.0
        # Straight
    elif is_straight:
        print("Straight!")
        return 5 + is_straight / 100.0
        # 3 of a kind
    elif is_three_kind:
        print("Three of a Kind!")
        return 4 + is_three_kind / 100.0
        # 2 pair
    elif is_two_pairs:
        print("Two Pairs!")
        return 3 + is_two_pairs / 100.0
    elif is_one_pair:
        print("Pair!")
        return 2 + is_one_pair / 100.0
    else:
        return 1 + highcard(cards) / 100
