import unittest
import mines

# Non-ui tests.

class levelTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_level(self):
        self.assertEqual(mines.getLevel(), mines.level)

class fileTests(unittest.TestCase):
    def setUp(self):
        self.highscores = mines.highscores

    def tearDown(self):
        mines.highscores = self.highscores
        mines.setUp(mines.level)

    def test_read_highscores_emptypath(self):
        self.assertEqual(mines.readHighscores(''), {})

    def test_read_configuration_emptypath(self):
        self.assertEqual(mines.readConfiguration(''), {})

    def test_write_highscores_emptypath(self):
        self.assertEqual(mines.setHighScores(''), None)

    def test_read_highscores_nopath(self):
        with self.assertRaises(TypeError):
            mines.readHighscores()

    def test_read_configuration_nopath(self):
        with self.assertRaises(TypeError):
            mines.readConfiguration()

    def test_write_highscores_nopath(self):
        with self.assertRaises(TypeError):
            mines.setHighScores()

class highscoreTests(unittest.TestCase):

    def setUp(self):
        self.highscores = mines.highscores
        self.level = mines.level

    def tearDown(self):
        mines.level = self.level
        mines.highscores = self.highscores
        mines.setUp(mines.level)

    def test_add_highscore(self):
        mines.highscores = {}
        mines.setUp(level='easy')
        test_time = '00:16'
        mines.statusTimeVar.set(test_time)
        mines.addHighscore()
        self.assertIsInstance(mines.highscores['easy'], list)
        self.assertEqual(mines.highscores['easy'][0]['score'], test_time)


if __name__ == '__main__':
    unittest.main(verbosity=2)
