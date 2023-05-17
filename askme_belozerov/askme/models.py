QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'text': f'Text {i}'
    } for i in range(15)
]

TAGS = [
    {
        'id': i,
        'title': f'Question {i}',
        'name': f'Text{i}',
        'text': f'Text {i}'
    } for i in range(2)
]


ANSWERS = [
    {
        'id': i,
        'text': f'Text: {i}',
        'tag' : TAGS[0],
    } for i in range(3)
]