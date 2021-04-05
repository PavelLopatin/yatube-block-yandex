from django.test import TestCase
from ..models import Group, Post, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Описание',
            slug='test-task')

        cls.post = Post.objects.create(
            author=User.objects.create(username='Pavel'),
            text='Тестовый текст',
            group=cls.group)

    def test_verbose_name(self):
        post = PostsModelTest.post
        field_verboses = {
            'group': 'Выберите группу',
            'text': 'Текст поста'}

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostsModelTest.post
        field_help_texts = {
            'group': 'Выберите группу из перечисленных, либо пропустите поле',
            'text': 'Введите текст'}

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str(self):
        post = PostsModelTest.post
        text = post.text
        self.assertEquals(str(post), text[:15])

    def test_str_title(self):
        group = PostsModelTest.group
        title = group.title
        self.assertEqual(title, str(group))
