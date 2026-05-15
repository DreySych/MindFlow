from abc import ABC, abstractmethod
from questions.models import Question


class SearchStrategy(ABC):
    """ Общий интерфейс для разных алгоритмов ИИ-поиска вопросов. """
    @abstractmethod
    def get_questions(self, query):
        """ Возвращает коллекцию вопросов, которые пойдут в контекст для ИИ. """
        raise NotImplementedError


class AllQuestionsStrategy(SearchStrategy):
    """ Берём все вопросы. """

    def get_questions(self, query):
        return Question.objects.all()


class LastNQuestionsStrategy(SearchStrategy):
    """ Берём только последние n вопросов. """

    def __init__(self, n):
        self.n = n

    def get_questions(self, query):
        return Question.objects.order_by("-creation_date")[: self.n]
