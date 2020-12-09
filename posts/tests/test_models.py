from django.test import TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            username='testuser', password='testuser'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа', description='Группа для тестов'
        )
        cls.post = Post.objects.create(
            author=cls.user, group=cls.group, text='Тестовый постТестовый пост'
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'group': 'Группа',
            'text': 'Текст',
            'pub_date': 'Дата выпуска',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_helps = {
            'author': 'Имя автора',
            'group': 'Название группы',
            'text': 'Опишите суть поста',
            'pub_date': 'Дата выпуска',
        }

        for value, expected in field_helps.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_object_name_is_field(self):
        """В поле __str__  объекта post записано значение поля post.text[:15]"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(title='Тестовая группа', description='Тестовое описание'
                                         )

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
            'slug': 'Адрес для страницы группы',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        group = GroupModelTest.group
        field_helps = {
            'title': 'Дайте короткое название заголовку',
            'description': 'Дайте короткое описание группе',
            'slug': ('Укажите адрес для страницы группы. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
        }

        for value, expected in field_helps.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )

    def test_object_name_is_title_field(self):
        """В поле __str__  объекта task записано значение поля task.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
