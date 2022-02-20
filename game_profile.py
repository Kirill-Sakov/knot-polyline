"""
Performance profiling.
To print application performance data to the console,
wrap the Game.run() function in a decorator @profile_game
"""
import cProfile
import pstats


def profile_game(func, sort='cumtime'):
    """Decorator of profile function"""
    def wrap(self):
        profiler = cProfile.Profile()
        profiler.enable()
        func(self)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats(sort)
        stats.print_stats()
    return wrap
