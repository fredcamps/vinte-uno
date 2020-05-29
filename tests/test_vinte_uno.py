"""Tests for `vinte_uno` package."""
# pylint: disable=redefined-outer-name
from typing import Dict, Tuple

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
def fixture_gamblers() -> Tuple[vinte_uno.Gambler, ...]:
    """Returns a set of Gambler objects.

    :return: a tuple of 3 Gambler objects.
    :rtype: Tuple[vinte_uno.Gambler]
    """
    return (
        vinte_uno.Gambler(credit=1),
        vinte_uno.Gambler(credit=1),
        vinte_uno.Gambler(credit=1),
    )


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
    gambler = vinte_uno.Gambler()
    gambler.state = vinte_uno.GAMING
    gambler.state = vinte_uno.STAYED
    gambler.hit(deck=deck)
    dealer = vinte_uno.Dealer()
    dealer.state = vinte_uno.HIDING
    dealer.hit(deck=deck)

    assert gambler.hand == 0
    assert dealer.hand == 0


def test_gambler_should_play_game() -> None:
    """Test if gambler should change from ready to game to gaming state.
    """
    gambler = vinte_uno.Gambler()
    previous = gambler.state
    gambler.hit(deck=vinte_uno.Deck())
    gambler.play()

    assert previous == vinte_uno.READY_TO_GAME
    assert gambler.state == vinte_uno.GAMING


def test_gambler_should_not_play_game() -> None:
    """Test if gambler should not change from ready to game to gaming state.
    """
    gambler = vinte_uno.Gambler()
    gambler.play()

    assert gambler.state == vinte_uno.READY_TO_GAME


def test_gambler_should_bust(fixture_hand: pytest_mock.plugin.MockFixture) -> None:
    """Test if gambler should bust.

    :param fixture_hand: object that contains a mocked fixture hand
    :type fixture_hand: pytest_mock.plugin.MockFixture
    """
    fixture_hand.return_value = 22
    gambler = vinte_uno.Gambler()
    gambler.state = vinte_uno.GAMING
    gambler.bust()

    assert gambler.state == vinte_uno.BUSTED


def test_gambler_should_not_bust() -> None:
    """Test if gambler should not bust.

    """
    gambler = vinte_uno.Gambler()
    gambler.state = vinte_uno.GAMING
    gambler.bust()

    assert gambler.state == vinte_uno.GAMING


def test_gambler_should_tweenty_one(fixture_hand: pytest_mock.plugin.MockFixture) -> None:
    """Test if gambler should win the match with tweenty one rank points.

    :param fixture_hand: object that contains a mocked fixture hand
    :type fixture_hand: pytest_mock.plugin.MockFixture

    """
    fixture_hand.return_value = 21
    gambler = vinte_uno.Gambler()
    gambler.state = vinte_uno.GAMING
    gambler.win()

    assert gambler.state == vinte_uno.TWENTY_ONE


def test_gambler_should_not_tweenty_one() -> None:
    """Test if gambler should not win the match with 21 rank points.

    """
    gambler = vinte_uno.Gambler()
    gambler.state = vinte_uno.GAMING
    gambler.win()

    assert gambler.state == vinte_uno.GAMING


def test_gambler_should_stay() -> None:
    """Test if gamble should stays.
    """
    gambler = vinte_uno.Gambler()
    gambler.state = vinte_uno.GAMING
    gambler.stay()

    result = gambler.state

    assert result == vinte_uno.STAYED


def test_dealer_turn_should_deal(fixture_gamblers: Tuple[vinte_uno.Gambler, ...]) -> None:
    """Test if all dealer turn should deal.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer()

    assert all(gambler.state == vinte_uno.READY_TO_GAME for gambler in gamblers)
    assert dealer.state == vinte_uno.DEAL_PENDING

    dealer.turn(gamblers=set(gamblers))

    assert all(gambler.state == vinte_uno.GAMING for gambler in gamblers)
    assert dealer.state == vinte_uno.STARTED


def test_dealer_turn_should_hide(fixture_gamblers: Tuple[vinte_uno.Gambler, ...]) -> None:
    """Test if all dealer turn should hide.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer()
    dealer.turn(gamblers=set(gamblers))
    dealer.turn(gamblers=set(gamblers))
    assert dealer.state == vinte_uno.HIDING


def test_dealer_turn_should_expose(  # noqa:WPS218
    fixture_gamblers: Tuple[vinte_uno.Gambler, ...],  # pylint: disable=bad-continuation
    fixture_hand: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should expose.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    :param fixture_hand: A set with gambler objects in initial state
    :type fixture_hand: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer(credit=1)
    fixture_hand.return_value = 0
    dealer.turn(gamblers=set(gamblers))
    fixture_hand.return_value = 5
    dealer.turn(gamblers=set(gamblers))

    fixture_hand.return_value = 12
    gamblers[0].state = vinte_uno.STAYED
    gamblers[1].state = vinte_uno.TWENTY_ONE
    gamblers[2].state = vinte_uno.BUSTED
    dealer.turn(gamblers=set(gamblers))

    assert dealer.state == vinte_uno.EXPOSED


def test_dealer_should_stay_after_expose(  # noqa:WPS218
    fixture_gamblers: Tuple[vinte_uno.Gambler, ...],  # pylint: disable=bad-continuation
    fixture_hand: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should stay after expose.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    :param fixture_hand: A set with gambler objects in initial state
    :type fixture_hand: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer(credit=1)
    fixture_hand.return_value = 0
    dealer.turn(gamblers=set(gamblers))
    fixture_hand.return_value = 10
    dealer.turn(gamblers=set(gamblers))

    fixture_hand.return_value = 21
    gamblers[0].state = vinte_uno.STAYED
    gamblers[1].state = vinte_uno.TWENTY_ONE
    gamblers[2].state = vinte_uno.BUSTED
    dealer.turn(gamblers=set(gamblers))

    assert dealer.state == vinte_uno.STAYED


def test_dealer_turn_should_stay(  # noqa:WPS218
    fixture_gamblers: Tuple[vinte_uno.Gambler, ...],  # pylint: disable=bad-continuation
    fixture_hand: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should stay.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    :param fixture_hand: A set with gambler objects in initial state
    :type fixture_hand: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer()
    fixture_hand.return_value = 0
    dealer.turn(gamblers=set(gamblers))
    fixture_hand.return_value = 5
    dealer.turn(gamblers=set(gamblers))
    gamblers[0].state = vinte_uno.STAYED
    gamblers[1].state = vinte_uno.TWENTY_ONE
    gamblers[2].state = vinte_uno.BUSTED
    fixture_hand.return_value = 12
    dealer.turn(gamblers=set(gamblers))
    fixture_hand.return_value = 20
    dealer.turn(gamblers=set(gamblers))

    assert dealer.state == vinte_uno.STAYED


def test_dealer_turn_should_bust(  # noqa:WPS218
    fixture_gamblers: Tuple[vinte_uno.Gambler, ...],  # pylint: disable=bad-continuation
    fixture_hand: pytest_mock.plugin.MockFixture,  # pylint: disable=bad-continuation
) -> None:
    """Test if dealer turn should bust.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    :param fixture_hand: A set with gambler objects in initial state
    :type fixture_hand: pytest_mock.plugin.MockFixture
    """
    gamblers = fixture_gamblers
    dealer = vinte_uno.Dealer()
    fixture_hand.return_value = 0
    dealer.turn(gamblers=set(gamblers))
    fixture_hand.return_value = 5
    dealer.turn(gamblers=set(gamblers))
    gamblers[0].state = vinte_uno.STAYED
    gamblers[1].state = vinte_uno.TWENTY_ONE
    gamblers[2].state = vinte_uno.BUSTED
    fixture_hand.return_value = 12
    dealer.turn(gamblers=set(gamblers))
    fixture_hand.return_value = 22
    dealer.turn(gamblers=set(gamblers))

    assert dealer.state == vinte_uno.BUSTED


def test_round_should_end_successfully(
    fixture_gamblers: Tuple[vinte_uno.Gambler, ...],  # pylint: disable=bad-continuation
) -> None:
    """Test if round should end successfully.

    :param fixture_gamblers: A tuple with gambler objects in initial state
    :type fixture_gamblers: Tuple[vinte_uno.Gambler, ...]
    """
    gamblers = set(fixture_gamblers)
    match = vinte_uno.Match()
    match.start(
        gamblers=gamblers,
        dealer=vinte_uno.Dealer(credit=1),
    )
