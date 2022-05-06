import datetime
from urllib import response

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Choice, Question

class QuestionModelTests(TestCase):

    def test_was_published_recently_for_future_question(self):
        """
        was_published_recently() should return false for questions, whose
        date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_questions(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

def create_choices_for_question(question, choices):
    """
    Create a set of choices with votes for a question.
    """
    choice_list = []
    for choice in choices:
        choice_list.append(Choice.objects.create(
            choice_text=choice['choice_text'],
            votes=choice['votes'],
            question=question ))
    return choice_list


class QuestionIndexViewTests(TestCase):

    def test_no_question(self):
        """
        If no questions exist, an appropriate message is displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on
        the index page.
        """
        question = create_questions(question_text="Past Question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )
    
    def test_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed
        on the index page.
        """
        create_questions(question_text="Future Question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def test_past_and_future_question(self):
        """
        If both past and future questions exist, only the past questions
        should be shown on the index page.
        """
        create_questions(question_text="Future Question", days=30)
        question = create_questions(question_text="Past Question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_multiple_past_questions(self):
        """
        The index page should show multiple questions
        """
        question = create_questions(question_text="Past Question.", days=-30)
        question1 = create_questions(question_text="Past Question 1.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question1, question]
        )

class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        The detail view of a question set in the future should return a
        404 not found page.
        """
        future_question = create_questions(question_text="Future Question.", days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question set in the past should return 
        the question's details, such as the question text.
        """
        past_question = create_questions(question_text="Past Question.", days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsViewTests(TestCase):

    def test_future_question(self):
        """
        The results view of a question set in the future should return a
        404 not found page.
        """
        future_question = create_questions(question_text="Future Question.", days=30)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        The results view of a question set in the past should return 
        the polls's results.
        """
        past_question = create_questions(question_text="Past Question.", days=-5)
        past_question_choice_set = past_question.choice_set.all()
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        
        for choice in past_question_choice_set:
            self.assertContains(response, choice.choice_text)
            self.assertContains(response, choice.votes)

        self.assertContains(response, past_question.question_text)

    def test_choice_creation(self):
        """
        Ensure choices are added correctly to a question
        """
        question = create_questions(question_text="What is going on?", days=-5)
        choice_list = [
            {
                'choice_text': 'Nothing.',
                'votes': 20
            },
            {
                'choice_text': 'Nothing but in green.',
                'votes': 31
            }
        ]
        create_choices_for_question(question=question, choices=choice_list)
        url = reverse('polls:results', args=(question.id,))
        response = self.client.get(url)

        self.assertContains(response, question.question_text)

        for choice in choice_list:
            self.assertContains(response, choice['choice_text'])
            self.assertContains(response, choice['votes'])
    
