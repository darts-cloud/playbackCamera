import unittest
from playbackCamera.player.BasePlayer import BasePlayer

class TestBasePlayer(unittest.TestCase):

    def test_base_player(self):
        player = BasePlayer()
        player.start()
        self.assertFalse(player.stopped)
        player._endProcess()
        self.assertTrue(player.stopped)

if __name__ == '__main__':
    unittest.main()