from ticket.models.models import Filter


def test_filter():
    ft = Filter()
    assert not bool(ft.domain)
