# test_forms.py
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from yatube import settings

from ..models import Group, Post, User
import shutil


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Федор')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Тестовая группа',
        )

        cls.post = Post.objects.create(
            text='Нередактированный пост',
            group=PostCreateFormTests.group,
            author=PostCreateFormTests.user,
        )

    def test_new_post_created_from_form_data(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': PostCreateFormTests.group.id
        }
        response = PostCreateFormTests.authorized_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Нередактированный пост',
                group=PostCreateFormTests.group.id
            ).exists())

    def test_edit_post_by_form(self):
        """Проверка редактирования поста через форму"""
        posts_count = Post.objects.count()
        form_fields = {
            'text': 'пост'}

        response = self.authorized_client.post(
            reverse('post_edit',
                    kwargs={'username': self.user,
                            'post_id': self.post.id}),
            data=form_fields, follow=True)

        self.assertRedirects(response, reverse('post',
                             kwargs={'username': self.user,
                                     'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'пост')


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR,
                                               prefix='test_')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст для теста',
            group=PostsCreateFormTests.group,
            author=User.objects.create(username='tester'),
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.get(username='tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        
    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
        form_data = {
            'group': PostsCreateFormTests.group.id,
            'text': 'Тестовый текст',
            'image': PostsCreateFormTests.uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('post_new'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                image='posts/small.gif',
            ).exists()
        )
