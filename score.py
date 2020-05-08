# from models import Card


def flush(cards):
    suits = []
    for card in cards:
        if card.suit not in suits:
            suits.append(card.suit)
    if len(suits) == 1:
        hc = 0
        for card in cards:
            if card.number > hc:
                hc = card.number
        return hc
    return False


def straight(cards):
    number = []
    for card in cards:
        if card.number not in number:
            number.append(card.number)
    number.sort()
    if not len(number) == 5:
        return False
    if number[4] == 14 and number[3] == 5 and number[2] == 4 and number[1] == 3 and number[0] == 2:  # Ace though 5 straight
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
    number = []
    for card in cards:
        number.append(card.number)
    for value in number:
        if number.count(value) == 4:
            return value
    return False


def threeKind(cards):
    number = []
    for card in cards:
        number.append(card.number)
    for value in number:
        if number.count(value) == 3:
            return value
    return False


def pairs(cards):
    pairs = []
    number = []
    for card in cards:
        number.append(card.number)
    for value in number:
        if number.count(value) == 2 and value not in pairs:
            pairs.append(value)
    return pairs


def twoPairs(cards):
    pair = pairs(cards)
    if len(pair) == 2:
        return max(pair[0], pair[1]) + min(pair[0], pair[1]) / 100.0
    else:
        return False


def onePair(cards):
    pair = pairs(cards)
    if len(pair) == 1:
        return pair[0]
    else:
        return False


def highcard(cards):
    number = []
    highcard = 0
    for card in cards:
        number.append(card.number)
    number.sort(reverse=True)
    divisor = 100.0
    for card in number:
        highcard = highcard + card / divisor
        divisor = divisor * 100.0
    return highcard


def pokerScore(cards):
    is_straight = straight(cards)
    is_flush = flush(cards)
    is_one_pair = onePair(cards)
    is_two_pairs = twoPairs(cards)
    is_three_kind = threeKind(cards)
    is_fourKind = fourKind(cards)

    num_cards = len(cards)
    if num_cards <= 5:
        if num_cards == 5: 
            # Royal flush
            if is_straight and is_flush and is_straight == 14:
                message = "Royal Flush!!!"
                return 10, message
            # Straight flush
            elif is_straight and is_flush:
                message = "Straight Flush!"
                return 9 + is_straight / 100.0, message
            # 4 of a kind
            elif is_fourKind:
                message = "Four of a kind!"
                return 8 + is_fourKind / 100.0, message
            # Full House
            elif is_three_kind and is_one_pair:
                message = "Full House!"
                return 7 + is_three_kind / 100.0, message
            # Flush
            elif is_flush:
                message = "Flush!"
                return 6 + is_flush / 100.0, message
            # Straight
            elif is_straight:
                message = "Straight!"
                return 5 + is_straight / 100.0, message
        elif num_cards == 4:
            # 4 of a kind
            if is_fourKind:
                message = "Four of a kind!"
                return 8 + is_fourKind / 100.0, message
        # 3 of a kind
        if is_three_kind:
            message = "Three of a Kind!"
            return 4 + is_three_kind / 100.0, message
        # 2 pair
        elif is_two_pairs:
            message = "Two Pairs!"
            return 3 + is_two_pairs / 100.0, message
        elif is_one_pair:
            message = "Pair!"
            return 2 + is_one_pair / 100.0, message
        else:
            message = "High Card"
            return 1 + highcard(cards), message
    else: # for n > 5 cards, remove any 1 card and recursively call for n-1 cards
        score = 0
        for i in range(len(cards)):
            new_cards = cards.copy()
            new_cards.pop(i)
            new_score, new_message = pokerScore(new_cards)
            if new_score > score:
                score = new_score
                message = new_message
        return score, message
