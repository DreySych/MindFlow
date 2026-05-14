from django.test import TestCase, Client
from unittest.mock import patch
from django.utils import timezone
from users.models import User
from questions.models import Question, Comment, Answer


class QuestionsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        def create_user(name, active=True):
            return User.objects.create_user(
                username=name, password='pass', email=f'{name}@ex.com', sex=1,
                role='user', birth_date='2000-01-01',
                registration_date=timezone.now().date(), reputation=0, active=active
            )
        self.author = create_user('author')
        self.other = create_user('other')
        self.blocked = create_user('blocked', active=False)

        self.question = Question.objects.create(
            title='Test Question', description='Test description', author=self.author,
            creation_date=timezone.now(), images='', rating=0, embedding=''
        )
        self.comment = Comment.objects.create(
            text='Test comment', rating=0, author=self.author,
            creation_date=timezone.now(), question=self.question
        )

    def login(self, username):
        if username:
            self.client.login(username=username, password='pass')
        else:
            self.client.logout()

    @patch('questions.views.SentenceTransformer')
    def test_create_post_post_valid(self, mock_model):
        mock_model.return_value.encode.return_value = [[0.1, 0.2, 0.3]]
        self.login('author')
        response = self.client.post(
            '/question/make/', {'title': 'New Post', 'description': 'New desc'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Question.objects.filter(title='New Post').exists())

    @patch('questions.views.SentenceTransformer')
    def test_create_post_without_image(self, mock_model):
        mock_model.return_value.encode.return_value = [[0.1, 0.2, 0.3]]
        self.login('author')
        self.client.post('/question/make/',
                         {'title': 'No image post', 'description': 'Text'})
        post = Question.objects.get(title='No image post')
        self.assertEqual(post.images, '')

    @patch('questions.views.SentenceTransformer')
    def test_create_post_title_only(self, mock_model):
        mock_model.return_value.encode.return_value = [[0.1, 0.2, 0.3]]
        self.login('author')
        self.client.post('/question/make/', {'title': 'Just Title'})
        post = Question.objects.get(title='Just Title')
        self.assertEqual(post.description, '')

    def test_create_post_unauthenticated(self):
        response = self.client.get('/question/make/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/account/login'))

    def test_create_post_blocked_user(self):
        self.login('blocked')
        response = self.client.get('/question/make/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_edit_post_get_author(self):
        self.login('author')
        response = self.client.get(f'/question/edit/?id={self.question.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.title)

    def test_edit_post_post_author(self):
        self.login('author')
        response = self.client.post(f'/question/edit/?id={self.question.id}',
                                    {'title': 'Updated Title', 'description': 'Updated desc'})
        self.question.refresh_from_db()
        self.assertEqual(self.question.title, 'Updated Title')
        self.assertEqual(response.status_code, 302)

    def test_edit_post_other_user_forbidden(self):
        self.login('other')
        response = self.client.get(f'/question/edit/?id={self.question.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_edit_post_unauthenticated(self):
        response = self.client.get(f'/question/edit/?id={self.question.id}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_edit_post_blocked_user(self):
        self.login('blocked')
        response = self.client.get(f'/question/edit/?id={self.question.id}')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_create_comment_authenticated(self):
        self.login('other')
        response = self.client.post(
            f'/question/{self.question.id}/', {'text': 'My new comment'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='My new comment').exists())

    def test_create_comment_unauthenticated(self):
        response = self.client.post(
            f'/question/{self.question.id}/', {'text': 'No auth comment'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_create_comment_blocked_user(self):
        self.login('blocked')
        response = self.client.post(
            f'/question/{self.question.id}/', {'text': 'Blocked comment'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_create_answer_to_comment(self):
        self.login('other')
        response = self.client.post(
            f'/comment/{self.comment.id}/answer/', {'text': 'Answer text'})
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.filter(answer='Answer text').first()
        self.assertIsNotNone(answer)
        self.assertEqual(answer.comment, self.comment)

    def test_answer_unauthenticated(self):
        response = self.client.post(
            f'/comment/{self.comment.id}/answer/', {'text': 'No auth'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_like_comment(self):
        self.login('other')
        response = self.client.get(
            f'/comment/like/?id={self.comment.id}',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], 1)

    def test_dislike_comment(self):
        self.login('other')
        response = self.client.get(
            '/comment/dislike/?id=' + str(self.comment.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], -1)

    def test_like_comment_unauthenticated(self):
        response = self.client.get(
            '/comment/like/?id=' + str(self.comment.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('login', data)

    def test_like_comment_blocked(self):
        self.login('blocked')
        response = self.client.get(
            '/comment/like/?id=' + str(self.comment.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertEqual(
            data['error'], 'Вы заблокированы и не можете выполнять это действие')

    def test_like_answer(self):
        answer = Answer.objects.create(
            answer='Test answer',
            author=self.author,
            rating=0,
            creation_date=timezone.now(),
            comment=self.comment
        )
        self.login('other')
        response = self.client.get(
            '/answer/like/?id=' + str(answer.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], 1)

    def test_dislike_answer(self):
        answer = Answer.objects.create(
            answer='Test answer',
            author=self.author,
            rating=0,
            creation_date=timezone.now(),
            comment=self.comment
        )
        self.login('other')
        response = self.client.get(
            '/answer/dislike/?id=' + str(answer.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], -1)

    def test_like_answer_unauthenticated(self):
        answer = Answer.objects.create(
            answer='Test',
            author=self.author,
            rating=0,
            creation_date=timezone.now(),
            comment=self.comment
        )
        response = self.client.get(
            '/answer/like/?id=' + str(answer.id),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertFalse(data['ok'])

    def test_question_page_get(self):
        response = self.client.get(f'/question/{self.question.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.title)

    def test_question_page_invalid_id(self):
        response = self.client.get('/question/999999/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_question_page_with_comment_form(self):
        self.login('other')
        response = self.client.get(f'/question/{self.question.id}/')
        self.assertContains(response, 'id="commentForm"')

        # ТЕСТЫ ДЛЯ ЛАЙКОВ/ДИЗЛАЙКОВ ПОСТОВ (вопросов)

    def test_like_post_increases_rating(self):
        # Лайк поста незалогиненым пользователем запрещён -> залогиним другого и лайкнем
        self.login('other')
        response = self.client.get(
            f'/like/?id={self.question.id}',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], 1)

    def test_like_post_toggle_removes_like(self):
        # Повторный лайк снимает лайк и уменьшает рейтинг
        self.login('other')
        # Первый лайк
        self.client.get(f'/like/?id={self.question.id}',
                        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # Повторный лайк должен снять
        response = self.client.get(
            f'/like/?id={self.question.id}', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], 0)

    def test_dislike_post_decreases_rating(self):
        # Дизлайк уменьшает рейтинг
        self.login('other')
        response = self.client.get(
            f'/dislike/?id={self.question.id}', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], -1)

    def test_switch_dislike_to_like_changes_rating_correctly(self):
        # Переключение с дизлайка на лайк должно прибавить 2 к рейтингу
        self.login('other')
        # Сначала дизлайк
        self.client.get(
            f'/dislike/?id={self.question.id}', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        q = Question.objects.get(id=self.question.id)
        self.assertEqual(q.rating, -1)
        # Затем лайк - ожидание: рейтинг = +1 (из -1 + 2)
        response = self.client.get(
            f'/like/?id={self.question.id}', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['rating'], 1)

    def test_blocked_user_cannot_like(self):
        # Забаненный пользователь не может ставить лайки на посты
        self.login('blocked')
        response = self.client.get(
            f'/like/?id={self.question.id}', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertEqual(
            data['error'], 'Вы заблокированы и не можете выполнять это действие')
