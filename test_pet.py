from pet import Pet
import time


def test_initial_state():
    p = Pet(800, 200)
    assert p.state == 'walk'
    assert p.is_working
    assert p.y == 170


def test_work_cycle_starts_in_walk():
    p = Pet(800, 200)
    assert p.state == 'walk'
    assert p.vx != 0


def test_work_to_rest_transition():
    p = Pet(800, 200)
    p.work_timer = p.WORK_DURATION - 100
    p.update(200)
    assert not p.is_working
    assert p.state == 'sleep'


def test_rest_to_work_transition():
    p = Pet(800, 200)
    p.is_working = False
    p.rest_timer = p.REST_DURATION - 100
    p.state = 'sleep'
    p.update(200)
    assert p.is_working
    assert p.state == 'walk'


def test_click_during_work():
    p = Pet(800, 200)
    p.on_click()
    assert p.state == 'jump'
    assert p.get_speech() != ''


def test_click_during_rest():
    p = Pet(800, 200)
    p.is_working = False
    p.state = 'sleep'
    p.on_click()
    assert p.state == 'jump'


def test_drag_sequence():
    p = Pet(800, 200)
    p.on_drag_start()
    assert p.state == 'drag'
    p.on_drag_move(100, 100)
    assert p.x == 100
    p.on_drag_end(100, 100)
    assert p.state == 'walk'


def test_wall_bounce():
    p = Pet(800, 200)
    p.vx = -50
    p.facing_right = False
    p.x = 0
    p.update(33)
    assert p.vx > 0
    assert p.facing_right


def test_speed():
    p = Pet(800, 200)
    assert p.WALK_SPEED == 17.5


def test_drag_during_rest_returns_to_sleep():
    p = Pet(800, 200)
    p.is_working = False
    p.state = 'sleep'
    p.on_drag_end(400, 170)
    assert p.state == 'sleep'


if __name__ == '__main__':
    test_initial_state()
    test_work_cycle_starts_in_walk()
    test_work_to_rest_transition()
    test_rest_to_work_transition()
    test_click_during_work()
    test_click_during_rest()
    test_drag_sequence()
    test_wall_bounce()
    test_speed()
    test_drag_during_rest_returns_to_sleep()
    print('All tests passed!')
