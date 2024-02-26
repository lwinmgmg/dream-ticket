from ticket.models.filter import Filter


def test_filter():
    ft = Filter()
    assert not bool(ft.domain)
