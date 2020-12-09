import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='SitdikovR')
        cls.user2 = get_user_model().objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='тестовый заголовок',
            description='тестовое описание',
            slug='test-slug'
        )
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='тестовый текст',
            author=cls.user,
            group=Group.objects.get(slug='test-slug'),
            image=uploaded,
            id=1
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        site1 = Site(pk=1, domain='localhost:8000', name='localhost:8000')
        site1.save()
        flatpage_data = [
            {
                'url': '/about-author/',
                'title': 'about me',
                'content': '<b>content</b>'
            },
            {
                'url': '/about-spec/',
                'title': 'about my tech',
                'content': '<b>content</b>'
            },
            {
                'url': '/about-us/',
                'title': 'about my tech',
                'content': '<b>content</b>'
            }
        ]
        [
            FlatPage.objects.create(**data).sites.add(site1)
            for data in flatpage_data
        ]
        self.static_pages = ('/about-author/', '/about-spec/')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correctly_template(self):
        template_names = {
            'new.html': reverse('new_post'),
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  kwargs={'slug': self.group.slug}),
        }
        for template, reverse_name in template_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('index'))
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author
        post_group_0 = response.context.get('page')[0].group
        post_image_0 = response.context.get('page')[0].image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, self.post.image)
        self.assertTrue(len(response.context.get('page')) <= settings.POSTS_PER_PAGE)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': 'test-slug'}))
        group_title_0 = response.context.get(
            'group').title
        group_description_0 = response.context.get(
            'group').description
        group_slug_0 = response.context.get('group').slug
        group_image_0 = response.context.get('group').posts.get(id=1).image
        self.assertEqual(group_title_0, self.group.title)
        self.assertEqual(group_description_0, self.group.description)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_image_0, self.post.image)

    def test_new_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_username_post_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_username_post_view_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'post', kwargs={'username': self.user, 'post_id': self.post.id}))
        username_post = response.context.get('post')
        username_post_count = response.context.get('post_count')
        username_post_image = username_post.image
        self.assertEqual(username_post, self.post)
        self.assertEqual(username_post_count, 1)
        self.assertEqual(username_post_image, self.post.image)

    def test_username_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user}))
        profile_username = response.context.get('username')
        profile_post_count = response.context.get('paginator').count
        profile_page = response.context.get('page')
        self.assertTrue(len(profile_page) <= settings.POSTS_PER_PAGE)
        self.assertEqual(profile_username.username, self.user.username)
        self.assertEqual(profile_post_count, 1)
        self.assertEqual(profile_page[0].image, self.post.image)

    def test_about_spec_show_correct_context(self):
        response = self.authorized_client.get('/about-spec/')
        about_spec_title = response.context['flatpage'].title
        about_spec_content = response.context['flatpage'].content
        self.assertEqual(about_spec_title, 'about my tech')
        self.assertEqual(about_spec_content, '<b>content</b>')

    def test_about_author_show_correct_context(self):
        response = self.authorized_client.get('/about-author/')
        about_author_title = response.context['flatpage'].title
        about_author_content = response.context['flatpage'].content
        self.assertEqual(about_author_title, 'about me')
        self.assertEqual(about_author_content, '<b>content</b>')

    def test_group_post_exists_on_group_page(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug}))
        post = response.context.get('group').posts.all()[0]
        post_text = post.text
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post.group.id, self.group.id)

    def test_group_post_exists_on_main_page(self):
        response = self.authorized_client.get(reverse('index'))
        post = response.context.get('page')[0]
        self.assertEqual(post.text, self.post.text)

    def test_auth_can_follow_and_unfollow(self):
        self.authorized_client.get(
            reverse('profile_follow', args=('test-user',)))
        self.assertTrue(self.user.follower.count() == 1)
        self.authorized_client.get(
            reverse('profile_unfollow', args=('test-user',)))
        self.assertTrue(self.user.follower.count() == 0)

    def test_follow_shows_correct_post(self):
        self.authorized_client2.get(
            reverse('profile_follow', args=('SitdikovR',)))
        response = self.authorized_client2.get(reverse('follow_index'))
        follow_post = response.context.get('page')[0]
        self.assertEqual(follow_post.text, self.post.text)
        self.assertEqual(follow_post.author, self.user)
        self.assertEqual(follow_post.group, self.group)

        self.authorized_client2.get(
            reverse('profile_unfollow', args=('SitdikovR',)))
        response = self.authorized_client2.get(reverse('follow_index'))
        self.assertTrue(len(response.context.get('page')) == 0)
