def test_sample(tmp_dir):
    sample_file = (tmp_dir / 'sample.txt')
    print(f'touching {str(sample_file)!r}')
    sample_file.touch()
