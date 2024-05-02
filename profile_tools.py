import cProfile
import io
import pstats


def profile(function, args={}, path=None):
    """Profiles a function and saves the result in a file.

    Args:
        function (function): function profiled.
        args (dict): function arguments.
        path (str): path of the output file.

    """
    cp = cProfile.Profile()
    cp.enable()
    function(**args)
    if path is None:
        path = f"profile_{function.__name__}.txt"
    _write_profile_to_file(cp, path=path)
    filename = 'profile.prof'  # You can change this if needed
    cp.dump_stats(filename)


def _write_profile_to_file(c_profile_object, path, time_ordered=True):
    """Profiles a function and saves the result in the given path.

    Args:
        c_profile_object (cProfile.Profile): Profiler object.
        path (str): path of the output file.
        time_ordered (bool): Whether to sort the result.

    """
    c_profile_object.disable()
    string_io = io.StringIO()
    if time_ordered:
        ps = pstats.Stats(c_profile_object, stream=string_io)
        ps = ps.sort_stats(pstats.SortKey.CUMULATIVE)
    ps.print_stats()
    with open(path, "w", encoding="UTF-8") as handle:
        handle.write(string_io.getvalue())
