from pet import Pet


def test_initial_state():
    p = Pet()
    assert p.state == 'idle'


def test_state_cycle_order():
    p = Pet()
    assert p.state == 'idle'
    p.on_click()
    assert p.state == 'walk'
    p.on_click()
    assert p.state == 'angry'
    p.on_click()
    assert p.state == 'idle'


def test_timer_advances_state():
    p = Pet()
    p._state_timer = p.STATE_DURATION - 100
    p.update(200)
    assert p.state == 'walk'
    assert p._state_timer == 0.0


def test_timer_multiple_cycles():
    p = Pet()
    for _ in range(6):
        p._state_timer = p.STATE_DURATION - 100
        p.update(200)
    assert p.state == 'idle'


def test_state_changed_signal():
    received = []
    p = Pet()
    p.stateChanged.connect(received.append)
    p.on_click()
    assert received == ['walk']
    p.on_click()
    assert received == ['walk', 'angry']
    p.on_click()
    assert received == ['walk', 'angry', 'idle']


if __name__ == '__main__':
    test_initial_state()
    test_state_cycle_order()
    test_timer_advances_state()
    test_timer_multiple_cycles()
    test_state_changed_signal()
    print('All tests passed!')
