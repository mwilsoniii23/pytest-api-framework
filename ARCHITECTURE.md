8/14/2026
I wrote this test and it's failing (and I'm not sure why it's failing):

'''
def test_unknown_booker_variable_raises_validation_error(monkeypatch):
    monkeypatch.setenv("BOOKER_UNKNOWN_SETTING", "surprise")

    with pytest.raises(ValidationError):
        Settings()
'''

tests\unit\test_settings.py:50 (test_unknown_booker_variable_raises_validation_error)
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x00000230B2A50B50>
    def test_unknown_booker_variable_raises_validation_error(monkeypatch):
        monkeypatch.setenv("BOOKER_UNKNOWN_SETTING", "surprise")

      with pytest.raises(ValidationError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValidationError
tests\unit\test_settings.py:54: Failed