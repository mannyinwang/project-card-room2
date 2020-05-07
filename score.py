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
        return max(pair[0], pair[1])
    else:
        return False


def onePair(cards):
    pair = pairs(cards)
    if len(pair) == 1:
        return pair[0]
    else:
        return False


def highcard(cards):
    highcard = None
    for card in cards:
        if highcard is None:
            highcard = card.number
        elif card.number > highcard:
            highcard = card.number
    return highcard


def poker5CardScore(cards):
    print(cards)
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
        print("High Card")
        return 1 + highcard(cards) / 100


def poker6CardScore(cards):
    score = 0
    for i in range(len(cards)):
        new_cards = cards.copy()
        new_cards.pop(i)
        new_score = poker5CardScore(new_cards)
        if new_score > score:
            score = new_score
    return score


def poker7CardScore(cards):
    score = 0
    for i in range(len(cards)):
        new_cards = cards.copy()
        new_cards.pop(i)
        new_score = poker6CardScore(new_cards)
        if new_score > score:
            score = new_score
    return score


def pokerScore(cards):
    if len(cards) == 5:
        score = poker5CardScore(cards)
    elif len(cards) == 7:
        score = poker7CardScore(cards)
    return score


# hand1 = [{'number': 2,'suit': 1},{'number': 2,'suit': 2},{'number': 2,'suit': 3}, {'number': 2,'suit': 4}, {'number': 3,'suit': 1}]
# # print(hand[0])
# # print(hand[0].number)
# # print(flush(hand))
# hand2 = [{'number': 2,'suit': 1},{'number': 3,'suit': 1},{'number': 4,'suit': 1}, {'number': 5,'suit': 1}, {'number': 6,'suit': 1}]
# hand3 = [{'number': 2,'suit': 1},{'number': 3,'suit': 1},{'number': 4,'suit': 1}, {'number': 5,'suit': 1}, {'number': 14,'suit': 1}]
# hand4 = [{'number': 2,'suit': 2},{'number': 2,'suit': 1},{'number': 4,'suit': 4}, {'number': 4,'suit': 1}, {'number': 14,'suit': 1}]
# hand5 = [{'number': 2,'suit': 2},{'number': 3,'suit': 1},{'number': 4,'suit': 3}, {'number': 14,'suit': 1}, {'number': 14,'suit': 1}]
# hand6 = [{'number': 2,'suit': 3},{'number': 14,'suit': 1},{'number': 4,'suit': 2}, {'number': 14,'suit': 1}, {'number': 14,'suit': 1}]
# hand7 = [{'number': 2,'suit': 3},{'number': 13,'suit': 1},{'number': 4,'suit': 2}, {'number': 10,'suit': 1}, {'number': 14,'suit': 1}]
# # print(fourKind(hand1))
# # print(flush(hand1))
# # print(fourKind(hand2))
# # print(flush(hand2))
# # print(straight(hand1))
# # print(straight(hand2))
# # print(straight(hand3))
# # print(onePair(hand4))
# # print(onePair(hand5))
# # print(twoPairs(hand4))
# # print(twoPairs(hand5))
# # print(threeKind(hand5))
# # print(threeKind(hand6))
# # print(highcard(hand1))
# # print(highcard(hand6))
# print(hand1, pokerScore(hand1))
# print(hand2, pokerScore(hand2))
# print(hand3, pokerScore(hand3))
# print(hand4, pokerScore(hand4))
# print(hand5, pokerScore(hand5))
# print(hand6, pokerScore(hand6))
# print(hand7, pokerScore(hand7))