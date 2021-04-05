from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, Follow
from django import forms

User = get_user_model()


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')

        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание'
        )
        for number_post in range(16):
            Post.objects.create(
                text=f'Это {number_post} пост',
                author=cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
            'index.html': reverse('index'),
            'group.html': reverse('group', kwargs={'slug': self.group.slug}),
            'new.html': reverse('post_new')
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_count_post_in_index(self):
        """Проверка пагинатора. 10 из 16 постов на первой стр."""
        response = self.guest_client.get(reverse('index'))
        count_objects = len(response.context.get('page').object_list)
        self.assertEqual(count_objects, 10)


class ViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название',
            description='Тестовый текст',
            slug='test-task'
        )

        cls.post = Post.objects.create(
            text='Больше 15 символов',
            author=User.objects.create_user(username='test_user_for_post'),
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='test_user_for_post')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_edit_show_correct_context(self):
        """Проверяем context словарь post_edit"""
        response = self.authorized_client.get(
            reverse('post_edit',
                    kwargs={'username': self.post.author,
                            'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
    

class FollowTest(TestCase):
    def setUp(self):
        self.follower = User.objects.create_user(username='test')
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.user = User.objects.create_user(username='test_user_for_post')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_unfollow(self):
        """Тестируем отписку"""
        Follow.objects.create(user=self.follower, author=self.user)
        self.follower_client.get(
            reverse('profile_unfollow', kwargs={'username': self.user}))
        self.assertFalse( Follow.objects.filter(user=self.follower,
                                                author=self.user).exists())

    def test_follow(self):
        """Тестируем подписку"""
        Follow.objects.create(user=self.follower, author=self.user)
        self.follower_client.get(
            reverse('profile_follow', kwargs={'username': self.user}))
        self.assertTrue(Follow.objects.filter(user=self.follower,
                                              author=self.user).exists())
