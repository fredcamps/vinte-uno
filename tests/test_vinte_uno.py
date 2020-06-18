"""Tests for `vinte_uno` package."""
# pylint: disable=redefined-outer-name
from typing import Dict, List

import pytest
import pytest_mock

from vinte_uno import vinte_uno


@pytest.fixture()
def fixture_deck() -> Dict[str, int]:
    """Fixture with some deck data.

    :return: A dict with some deck data
    :rtype: Dict[str, int]
    """
    return {
        'length': 52,
    }


@pytest.fixture()
def fixture_gamblers() -> List[vinte_uno.Gambler]:
    """Returns a set of Gambler objects.

    :return: a tuple of 3 Gambler objects.
    :rtype: List[vinte_uno.Gambler]
    """
    return [
        vinte_uno.Gambler(credit=1, name='Gambler 1'),
        vinte_uno.Gambler(credit=1, name='Gambler 2'),
        vinte_uno.Gambler(credit=1, name='Gambler 3'),
    ]


@pytest.fixture()
def fixture_hand(mocker: pytest_mock.plugin.MockFixture) -> pytest_mock.plugin.MockFixture:
    """Fixture containing Dealer hand property fixture.

    :param mocker: Mock fixture
    :type: pytest_mock.plugin.MockFIxture

    :return: Fixture containing hand fixture
    :rtype: pytest_mock.plugin.MockFIxture
    """
    return mocker.patch.object(
        vinte_uno.Player,
        'hand',
        new_callable=mocker.PropertyMock,
    )


@pytest.fixture()
def fixture_deck_pick(mocker: pytest_mock.plugin.MockFixture) -> pytest_mock.plugin.MockFixture:
    """Fixture containing Deck pick mocked.

    :param mocker: Mock fixture
    :type: pytest_mock.plugin.MockFIxture

    :return: Fixture containing hand fixture
    :rtype: pytest_mock.plugin.MockFIxture
    """
    return mocker.patch.object(vinte_uno.Deck, 'pick')


def test_deck_should_arranged_properly(fixture_deck: Dict[str, int]) -> None:
    """Test if deck should arranged properly.

    :param fixture_deck: A dict with some deck data
    :type fixture_deck: Dict[str, int]
    """
    deck = vinte_uno.Deck()

    result = tuple(deck.cards)[0]

    assert isinstance(deck.cards, list)
    assert isinstance(result.image, str)
    assert len(result.image) > 1
    assert len(deck.cards) == fixture_deck.get('length')


def test_deck_card_should_picked(fixture_deck: Dict[str, int]) -> None:
    """Test if deck card should be picked.

    :param fixture_deck: A dict with some deck data
    :type fixture_deck: Dict[str, int]
    """
    deck = vinte_uno.Deck()

    result = deck.pick()

    assert len(deck.cards) == (fixture_deck.get('length') - 1)
    assert isinstance(result, vinte_uno.Card)


def test_deck_pick_should_raises_value_error() -> None:
    """Test if deck raises ValueError when try to pick a card.
    """
    deck = vinte_uno.Deck()
    deck.cards = []
    with pytest.raises(ValueError, match="Doesn't have enough cards!"):
        deck.pick()


def test_player_should_not_hit() -> None:
    """Test if player should not hit.
    """
    deck = vinte_uno.Deck()
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.state = vinte_uno.GAMING
    gambler.state = vinte_uno.STAYED
    gambler.hit(deck=deck)
    dealer = vinte_uno.Dealer(gamblers=[gambler])
    dealer.state = vinte_uno.HIDING
    dealer.hit(deck=deck)

    assert gambler.hand == 0
    assert dealer.hand == 0


def test_gambler_should_play_game() -> None:
    """Test if gambler should change from ready to game to gaming state.
    """
    gambler = vinte_uno.Gambler(name='Gambler')
    previous = gambler.state
    gambler.hit(deck=vinte_uno.Deck())
    gambler.play()

    assert previous == vinte_uno.READY_TO_GAME
    assert gambler.state == vinte_uno.GAMING


def test_gambler_should_not_play_game() -> None:
    """Test if gambler should not change from ready to game to gaming state.
    """
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.play()

    assert gambler.state == vinte_uno.READY_TO_GAME


def test_gambler_should_bust(fixture_hand: pytest_mock.plugin.MockFixture) -> None:
    """Test if gambler should bust.

    :param fixture_hand: object that contains a mocked fixture hand
    :type fixture_hand: pytest_mock.plugin.MockFixture
    """
    fixture_hand.return_value = 22
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.state = vinte_uno.GAMING
    gambler.bust()

    assert gambler.state == vinte_uno.BUSTED
    assert gambler.credit == 0


def test_gambler_should_not_bust() -> None:
    """Test if gambler should not bust.

    """
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.state = vinte_uno.GAMING
    gambler.bust()

    assert gambler.state == vinte_uno.GAMING


def test_gambler_should_tweenty_one(fixture_hand: pytest_mock.plugin.MockFixture) -> None:
    """Test if gambler should win the match with tweenty one rank points.

    :param fixture_hand: object that contains a mocked fixture hand
    :type fixture_hand: pytest_mock.plugin.MockFixture

    """
    fixture_hand.return_value = 21
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.state = vinte_uno.GAMING
    gambler.win()

    assert gambler.state == vinte_uno.TWENTY_ONE
    assert gambler.credit > 1

def test_gambler_should_not_tweenty_one() -> None:
    """Test if gambler should not win the match with 21 rank points.

    """
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.state = vinte_uno.GAMING
    gambler.win()

    assert gambler.state == vinte_uno.GAMING


def test_gambler_should_stay() -> None:
    """Test if gambler should stays.
    """
    gambler = vinte_uno.Gambler(name='Gambler')
    gambler.state = vinte_uno.GAMING
    gambler.stay()

    result = gambler.state

    assert result == vinte_uno.STAYED


def test_dealer_turn_should_stay_by_points(
    fixture_gamblers: List[vinte_uno.Gambler],  # pylint: disable=bad-continuation
    fixture_deck_pick: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should stay by non active gamblers states.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: List[vinte_uno.Gambler]
    :param fixture_deck_pick: A mocked Deck.pick() method
    :type fixture_deck_pick: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer(gamblers=gamblers)
    fixture_deck_pick.side_effect = [
        vinte_uno.Card(rank='10', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='ace', weight=1, suit='hearts', image=''),
        vinte_uno.Card(rank='9', weight=9, suit='nine', image=''),
        vinte_uno.Card(rank='queen', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='10', weight=10, suit='spades', image=''),
        vinte_uno.Card(rank='king', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='jack', weight=10, suit='diamonds', image=''),
        vinte_uno.Card(rank='9', weight=9, suit='clubs', image=''),
    ]
    dealer.turn()
    dealer.turn()
    gamblers[0].stay()
    gamblers[2].stay()
    dealer.turn()
    assert dealer.state == vinte_uno.STAYED
    assert gamblers[0].credit == 2
    assert gamblers[1].credit == 3
    assert gamblers[2].credit == 1


def test_dealer_turn_should_stay_by_gamblers(  # noqa:WPS218
    fixture_gamblers: List[vinte_uno.Gambler],  # pylint: disable=bad-continuation
    fixture_deck_pick: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should stay by non active gamblers states.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: List[vinte_uno.Gambler]
    :param fixture_deck_pick: A mocked Deck.pick() method
    :type fixture_deck_pick: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer(gamblers=gamblers)
    fixture_deck_pick.side_effect = [
        vinte_uno.Card(rank='10', weight=10, suit='diamonds', image=''),
        vinte_uno.Card(rank='ace', weight=1, suit='diamonds', image=''),
        vinte_uno.Card(rank='jack', weight=10, suit='diamonds', image=''),
        vinte_uno.Card(rank='queen', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='10', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='king', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='10', weight=10, suit='clubs', image=''),
        vinte_uno.Card(rank='6', weight=6, suit='clubs', image=''),
        vinte_uno.Card(rank='2', weight=2, suit='clubs', image=''),
        vinte_uno.Card(rank='2', weight=2, suit='spades', image=''),
    ]
    dealer.turn()
    dealer.turn()
    dealer.turn()

    assert dealer.state == vinte_uno.STAYED
    assert gamblers[0].credit == 0
    assert gamblers[1].credit == 3
    assert gamblers[2].credit == 0


def test_dealer_turn_should_bust(  # noqa:WPS218
    fixture_gamblers: List[vinte_uno.Gambler],  # pylint: disable=bad-continuation
    fixture_deck_pick: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should bust.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: List[vinte_uno.Gambler]
    :param fixture_deck_pick: A fixture with mocked deck pick
    :type fixture_deck_pick: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer(gamblers=gamblers)
    fixture_deck_pick.side_effect = [
        vinte_uno.Card(rank='10', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='ace', weight=1, suit='hearts', image=''),
        vinte_uno.Card(rank='jack', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='queen', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='5', weight=5, suit='hearts', image=''),
        vinte_uno.Card(rank='king', weight=10, suit='hearts', image=''),
        vinte_uno.Card(rank='10', weight=10, suit='diamonds', image=''),
        vinte_uno.Card(rank='6', weight=6, suit='diamonds', image=''),
        vinte_uno.Card(rank='2', weight=2, suit='diamonds', image=''),
        vinte_uno.Card(rank='8', weight=8, suit='diamonds', image=''),
    ]
    dealer.turn()
    dealer.turn()
    gamblers[0].stay()
    dealer.turn()
    dealer.turn()
    assert dealer.state == vinte_uno.BUSTED
    assert gamblers[0].state == vinte_uno.STAYED
    assert gamblers[1].state == vinte_uno.TWENTY_ONE
    assert gamblers[2].state == vinte_uno.BUSTED
    assert gamblers[0].credit == 2
    assert gamblers[1].credit == 3
    assert gamblers[2].credit == 0


def test_dealer_show_cards_correctly(
    fixture_gamblers: List[vinte_uno.Gambler],  # pylint: disable=bad-continuation
) -> None:
    """Test of dealer show cards correctly.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: List[vinte_uno.Gambler]
    """
    dealer = vinte_uno.Dealer(gamblers=fixture_gamblers)
    dealer.cards = [
        vinte_uno.Card(rank='8', weight=8, suit='diamonds', image=''),
        vinte_uno.Card(rank='10', weight=10, suit='spades', image=''),
        vinte_uno.Card(rank='ace', weight=1, suit='spades', image=''),
    ]
    dealer.state = vinte_uno.HIDING
    assert dealer.show() == [{
        'suit': 'diamonds',
        'rank': '8',
        'weight': 8,
        'image': '',
    }]
