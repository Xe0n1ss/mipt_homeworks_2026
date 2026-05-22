from final_project.core.history import ChatHistory


USER = 'user'
ASSISTANT = 'assistant'


def test_history_trims_by_message_count() -> None:
    history = ChatHistory(limit_message=2, limit_chars=None)
    history.add(USER, 'one')
    history.add(ASSISTANT, 'two')
    history.add(USER, 'three')

    assert [message.content for message in history.messages] == ['two', 'three']


def test_history_trims_by_chars() -> None:
    history = ChatHistory(limit_message=None, limit_chars=5)
    history.add(USER, 'abc')
    history.add(ASSISTANT, 'def')

    assert [message.content for message in history.messages] == ['def']


def test_history_cuts_single_long_message() -> None:
    history = ChatHistory(limit_message=None, limit_chars=4)
    history.add(USER, 'abcdef')

    assert history.messages[0].content == 'cdef'
