from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
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

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Andy')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_code_404(self):
        response = self.guest_client.get("/fdf/")
        self.assertEqual(response.status_code, 404)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_about_author_detail_url_exists_at_desired_location(self):
        """Страница /about/author/ доступна неавторизованному пользователю."""
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, 200)

    def test_about_author_detail_url_exists_at_desired_location(self):
        """Страница /about/tech/ доступна неавторизованному пользователю."""
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, 200)

    def test_group_detail_url_exists_at_desired_location_authorized(self):
        """Страница /task/test-slug/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(f"/group/{self.group.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_group_detail_url_exists_at_desired_location(self):
        """Страница /task/test-slug/ доступна неавторизованному пользователю"""
        response = self.guest_client.get(f"/group/{self.group.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_new_detail_url_exists_at_desired_location_authorized(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get("/new/")
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            f"/{self.post.author}/{self.post.id}/": "post.html",
            f"/{self.post.author}/": "profile.html",
            "/": "index.html",
            f"/group/{self.group.slug}/": "group.html",
            "/new/": "new.html"}

        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
