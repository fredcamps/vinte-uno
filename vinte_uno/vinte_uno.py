"""
This module contains the core functionality of this program.
"""
import random
from abc import ABCMeta
from typing import Dict, Iterator, List, NamedTuple, Set, Tuple

from transitions import Machine

TWENTY_ONE_RANK_POINTS = 21
ACE_RANK_POINTS = 11
DEALER_RANK_POINTS_LIMIT = 17
READY_TO_GAME = 'READY_TO_GAME'
GAMING = 'GAMING'
TWENTY_ONE = 'TWENTY_ONE'
BUSTED = 'BUSTED'
STAYED = 'STAYED'
DEAL_PENDING = 'DEAL_PENDING'
STARTED = 'STARTED'
HIDING = 'HIDING'
EXPOSED = 'EXPOSED'
START_PENDING = 'START_PENDING'
DEAL_PENDING = 'DEAL_PENDING'
BETS_PENDING = 'BETS_PENDING'
IN_PROCCESS = 'IN_PROCCESS'
FINISHED = 'FINISHED'
HIT_STATES = (
    DEAL_PENDING,
    READY_TO_GAME,
    GAMING,
    STARTED,
    EXPOSED,
)
# OUT_OF_ROUND_STATES = (
#     STAYED,
#     BUSTED,
#     TWENTY_ONE,
#     HIDING,
# )
GAMBLER_STATES = (
    READY_TO_GAME,
    GAMING,
    TWENTY_ONE,
    BUSTED,
    STAYED,
)
DEALER_STATES = (
    DEAL_PENDING,
    STARTED,
    HIDING,
    EXPOSED,
    BUSTED,
    STAYED,
)
MATCH_STATES = (
    BETS_PENDING,
    DEAL_PENDING,
    IN_PROCCESS,
    FINISHED,
)


class Card(NamedTuple):  # noqa: H601
    """Object that contains cards properties."""

    rank: str
    suit: str
    weight: int
    image: str


class Cards:
    """Object that generates set of cards.
    """

    def __init__(self) -> None:
        """Initializes Cards class.
        """
        self.suits: Set[str] = {'spades', 'clubs', 'diamond', 'hearts'}
        self.ranks: Set[Tuple[str, int]] = {
            ('ace', 1),
            ('2', 2),
            ('3', 3),
            ('4', 4),
            ('5', 5),
            ('6', 6),
            ('7', 7),
            ('8', 8),
            ('9', 9),
            ('10', 10),
            ('Jack', 10),
            ('Queen', 10),
            ('King', 10),
        }

    def _helper(self, suit: str) -> Iterator[Card]:
        rank_attrs = {}
        for rank in self.ranks:
            rank_attrs['string'] = str(rank[0])
            rank_attrs['weight'] = str(rank[1])
            image = '{0}-{1}.png'.format(rank_attrs['string'], suit)
            yield Card(
                suit=suit,
                rank=rank_attrs['string'],
                weight=int(rank_attrs['weight']),
                image=image,
            )

    def generate(self) -> Iterator[Card]:
        """Generates deck cards.

        :yield: A generator with Card objects
        :rtype: Iterator[Card]
        """
        for suit in self.suits:
            yield from self._helper(suit=suit)


class Deck:
    """Class that represents deck aggregating cards."""

    def __init__(self) -> None:
        """Instantiates this class."""
        self.cards: List[Card] = list(Cards().generate())

    def pick(self) -> Card:
        """Returns a card randomly and pick from deck.

        :raises ValueError: When not have cards on deck
        :return: A random card object
        :rtype: Card
        """
        max_index = len(self.cards)
        if max_index < 1:
            raise ValueError("Doesn't have enough cards!")
        index = random.SystemRandom().randint(0, max_index - 1)
        card = self.cards[index]
        self.cards.remove(card)
        return card


class Player(Machine, metaclass=ABCMeta):  # noqa: H601
    """Base class for Gambler and Dealer entities."""

    states: Tuple = ()

    def __init__(self, name: str, credit: int, amount: int = 0) -> None:
        """Instantiates this class.

        :param name: player name
        :param credit: represents a bet value
        :param amount: amount of credits on player account
        """
        super().__init__(model=self, states=list(self.states), initial=self.states[0])
        self.name = name
        self.cards: Set[Card] = set()
        self.credit = credit
        self.amount = amount

    @property
    def hand(self) -> int:
        """A property that contains total rank points on Player hand.

        :return: total rank points
        :rtype: int
        """
        if not self.cards:
            return 0

        have_ace = False
        rank_points = 0
        for card in self.cards:
            rank_points += card.weight
            if card.rank == 'ace':
                have_ace = True

        if rank_points == ACE_RANK_POINTS and have_ace:
            return ACE_RANK_POINTS + (rank_points - 1)

        return rank_points

    def hit(self, deck: Deck) -> None:
        """Player hits on game.

        :param deck: A deck object
        :type deck: Deck
        """
        if self.state in HIT_STATES:
            self.cards.add(deck.pick())

    def show(self) -> List[Dict[str, object]]:
        """Shows cards on player hands.

        :return: Returns a list with cards
        :rtype: List[Dict[str, object]]
        """
        cards = []
        for card in self.cards:
            cards.append(
                {
                    'suit': card.suit,
                    'rank': card.rank,
                    'weight': card.weight,
                    'image': card.image,
                },
            )

        return cards

    def should_bust(self) -> bool:
        """Condition for bust trigger.

        :return: A boolean value that satisfy condition or not
        :rtype: bool
        """
        return self.hand > TWENTY_ONE_RANK_POINTS


class Gambler(Player):
    """Class that represents gambler."""

    states: Tuple[str, ...] = GAMBLER_STATES

    def __init__(self, name: str = 'Gambler', credit: int = 1) -> None:
        """Initializes dealer class.

        :param name: Player name
        :param credit: int
        :type name: str
        :type credit: int
        """
        super().__init__(name=name, credit=credit)
        self.add_transition(
            trigger='play',
            source=READY_TO_GAME,
            dest=GAMING,
            conditions=['should_play'],
        )
        self.add_transition(
            trigger='win',
            source=GAMING,
            dest=TWENTY_ONE,
            conditions=['should_twenty_one'],
        )
        self.add_transition(trigger='stay', source=GAMING, dest=STAYED)
        self.add_transition(
            trigger='bust',
            source=GAMING,
            dest=BUSTED,
            conditions=['should_bust'],
        )

    def add_bet(self, credit: int) -> None:
        """Trigger method that starts a bet transition.

        :param credit: A number of bet credits
        :type credit: int
        """
        self.credit = credit
        self.bet()

    def should_play(self) -> bool:
        """Condition for play trigger.

        The Gambler only can play after the dealer deals
        cards.

        :return: A boolean value that satisfies condition or not
        :rtype: bool
        """
        return bool(self.cards)

    def should_twenty_one(self) -> bool:
        """Condition for twenty_one trigger.

        :return: A boolean value that satisfy condition or not
        :rtype: bool
        """
        return self.hand == TWENTY_ONE_RANK_POINTS


class Dealer(Player):
    """Class that represents dealer."""

    states: Tuple[str, ...] = DEALER_STATES

    def __init__(self, name: str = 'Dealer', credit: int = 1) -> None:
        """Initializes dealer class.

        :param name: Player name
        :param credit: Represents bet value
        :type name: str
        """
        super().__init__(name=name, credit=credit)
        self.credit: int = credit
        self.gamblers: Set[Gambler] = set()
        self.deck: Deck = Deck()
        self.add_transition(
            trigger='deal',
            source=DEAL_PENDING,
            dest=STARTED,
            conditions=['should_deal'],
            after=['after_deal'],
        )
        self.add_transition(
            trigger='hide',
            source=STARTED,
            dest=HIDING,
            conditions=['should_hide'],
        )
        self.add_transition(
            trigger='expose',
            source=HIDING,
            dest=EXPOSED,
            conditions=['should_expose'],
            after=['after_expose'],
        )
        self.add_transition(
            trigger='bust',
            source=EXPOSED,
            dest=BUSTED,
            conditions=['should_bust'],
        )
        self.add_transition(
            trigger='stay',
            source=EXPOSED,
            dest=STAYED,
            conditions=['should_stay'],
        )

    def _hit_for_gamblers(self, gamblers: Set[Gambler]) -> None:
        for gambler in gamblers:
            gambler.hit(deck=self.deck)
            if gambler.state == GAMING:
                gambler.bust()
                gambler.win()

        self.gamblers.update(gamblers)

    def turn(self, gamblers: Set[Gambler]) -> None:
        """Players hits a card and turns.

        :param gamblers: A set that contains gamblers
        :type gamblers: Set[Gambler]
        """
        self._hit_for_gamblers(gamblers)
        self.hit(deck=self.deck)
        states = {
            'DEAL_PENDING': self.deal,
            'STARTED': self.hide,
            'HIDING': self.expose,
            'EXPOSED': (self.bust, self.stay),
        }
        callable_trigger = states.get(self.state)
        if isinstance(callable_trigger, tuple) and self.hand > TWENTY_ONE_RANK_POINTS:
            callable_trigger[0]()
            return
        if isinstance(callable_trigger, tuple) and self.hand >= DEALER_RANK_POINTS_LIMIT:
            callable_trigger[1]()
            return

        callable_trigger()

    def should_deal(self) -> bool:
        """Condition for run deal trigger on state machine.

        :return: Condition
        :rtype: bool
        """
        for gambler in self.gamblers:
            if gambler.state != READY_TO_GAME:
                return False

        return all(_gambler.cards for _gambler in self.gamblers) and bool(self.cards)

    def after_deal(self) -> None:
        """Event that runs after deal trigger.
        """
        for gambler in self.gamblers:
            gambler.play()

    def after_expose(self) -> None:
        """Event that runs after expose trigger.

        It tries to stay after expose
        """
        self.stay()

    def should_hide(self) -> bool:
        """Condition for hide the last dealer card.

        :return: Condition for apply transition
        :rtype: bool
        """
        more_than_one = len(self.cards) > 1
        for gambler in self.gamblers:
            if gambler.state != GAMING or len(gambler.cards) <= 1:
                return False

        return more_than_one

    def should_expose(self) -> bool:
        """Condition for expose all dealer cards.

        :return: Condition for apply transition
        :rtype: bool
        """
        someone_stayed = False
        for gambler in self.gamblers:
            if gambler.state == GAMING:
                return False
            if gambler.state == STAYED:
                someone_stayed = True

        return someone_stayed

    def should_stay(self) -> bool:
        """Condition for dealer stays.

        :return: Condition for apply transition
        :rtype: bool
        """
        first_condition = (self.hand >= DEALER_RANK_POINTS_LIMIT)
        second_condition = (self.hand <= TWENTY_ONE_RANK_POINTS)
        return first_condition and second_condition

    def show(self) -> List[Dict[str, object]]:
        """Show cards on hand.

        :return: a list of dict containing hand cards
        :rtype: List[Dict[str, object]]
        """
        cards = super().show()
        if self.state == HIDING:
            return [cards[0]]

        return cards


class Match(Machine):
    """Class that represents a round/match."""

    states: Tuple[str, ...] = MATCH_STATES

    def __init__(self) -> None:
        """Initializes the match class."""
        super().__init__(model=self, states=self.states, initial=self.states[0])
        # self.add_transition(trigger='')
        # self.add_transition(trigger='')
        # self.add_transition(trigger='')

    def start(self, gamblers: Set[Gambler], dealer: Dealer) -> None:
        """Starts the round.

        :param gamblers: A set of gamblers that will play the game.
        :param dealer: The dealer object.
        :type gamblers: Set[Gambler]
        :type dealer: Dealer
        """
