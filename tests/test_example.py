from conftest import manual_test


def test_temp_file(tmp_dir):
    path = (tmp_dir / 'tmp.txt')
    print(f'touching {str(path)!r}')
    path.touch()


@manual_test
def test_user_input():
    input('Press enter to continue...')
