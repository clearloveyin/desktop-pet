from pet import Pet
import time

def test_initial_state():
    p = Pet(800, 600)
    assert p.state == 'idle'
    assert p.x == 400
    assert p.y == 300

def test_click_triggers_jump():
    p = Pet(800, 600)
    p.on_click()
    assert p.state == 'jump'
    assert p.state_duration == 600

def test_double_click():
    p = Pet(800, 600)
    p.on_double_click()
    assert p.state == 'jump'

def test_drag_sequence():
    p = Pet(800, 600)
    p.on_drag_start()
    assert p.state == 'drag'
    p.on_drag_move(100, 100)
    assert p.x == 100
    assert p.y == 100
    p.on_drag_end(100, 100)
    assert p.state == 'idle'

def test_drag_to_edge_hangs():
    p = Pet(800, 600)
    p.on_drag_end(5, 5)
    assert p.state == 'hang'

def test_sleep_after_timeout():
    p = Pet(800, 600)
    p.last_interaction_time = time.time() * 1000 - 20000
    p.update(100)
    assert p.state == 'sleep'

def test_click_wakes_from_sleep():
    p = Pet(800, 600)
    p.state = 'sleep'
    p.on_click()
    assert p.state == 'jump'

def test_chase_mouse():
    p = Pet(800, 600)
    p.on_mouse_near(50, 500)
    assert p.state == 'chase'
    p.update_chase_target(500, 300)
    assert p.vx > 0

def test_speech_bubble():
    p = Pet(800, 600)
    p.on_click()
    assert p.get_speech() != ''

def test_walk_transition():
    p = Pet(800, 600)
    p._start_walk()
    assert p.state == 'walk'

def test_update_with_timer():
    p = Pet(800, 600)
    p.state = 'walk'
    p.state_duration = 100
    p.state_timer = 0
    p.update(200)
    assert p.state == 'idle'

if __name__ == '__main__':
    test_initial_state()
    test_click_triggers_jump()
    test_double_click()
    test_drag_sequence()
    test_drag_to_edge_hangs()
    test_sleep_after_timeout()
    test_click_wakes_from_sleep()
    test_chase_mouse()
    test_speech_bubble()
    test_walk_transition()
    test_update_with_timer()
    print('All tests passed!')
