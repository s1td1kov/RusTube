from django.contrib.auth import get_user_model
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


class PostGroupURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='SitdikovR')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = get_user_model().objects.create_user(username='test-user')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        self.post = Post.objects.create(
            group=self.group, author=self.user, id=1, text='тестовый пост')

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

    def test_home_page_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_group_page_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, 200)

    def test_new_page_url_exists_at_desired_location(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_new_page_redirect_anonymous(self):
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_new_list_url_redirect_anonymous_on_auth_login(self):
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, reverse('login') +
                             '?next=' + reverse('new_post'))

    def test_users_correct_template(self):
        templates_url_name = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  kwargs={'slug': self.group.slug}),
            'new.html': reverse('new_post'),
            'profile.html': reverse('profile',
                                    kwargs={'username': self.user.username}),
            'post.html': reverse('post',
                                 kwargs={'username': self.user.username,
                                         'post_id': self.post.id}),
        }

        for template, reverse_name in templates_url_name.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_username_page_url_exists_at_desired_location(self):
        response = self.guest_client.get(
            reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_username_post_page_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_flatpage_about_author_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('about-us'))
        self.assertEqual(response.status_code, 200)

    def test_flatpage_about_spec_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse('about-spec'))
        self.assertEqual(response.status_code, 200)

    def test_guest_post_edit_url_exists_at_desired_location(self):
        response = self.guest_client.get(reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_author_post_edit_url_exists_at_desired_location(self):
        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_not_author_edit_url_exists_at_desired_location(self):
        response = self.authorized_client2.get(reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': self.post.id}))
        self.assertEqual(response.status_code, 302)

    def test_returns_404_if_doesnt_exist_page(self):
        response = self.authorized_client.get('/group/')
        self.assertEqual(response.status_code, 404)

    def test_post_url_redirects_correct_template_for_guest(self):
        response = self.guest_client.get(reverse('post_edit', kwargs={
                                         'username': self.user.username,
                                         'post_id': self.post.id}),
                                         follow=True)
        self.assertRedirects(response, reverse('login') + '?next=' +
                             reverse('post_edit', kwargs={
                                 'username': self.user.username,
                                 'post_id': self.post.id})
                             )

    def test_post_url_redirects_correct_template_not_author(self):
        response = self.authorized_client2.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}),
            follow=True)
        self.assertRedirects(response, reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': self.post.id}))

    def test_author_shows_correct_template(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}),
            follow=True)
        self.assertTemplateUsed(response, 'new.html')

    def test_not_author_shows_correct_template(self):
        response = self.authorized_client2.get(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': self.post.id}),
            follow=True)
        self.assertTemplateUsed(response, 'post.html')

    def test_only_auth_can_comment(self):
        response = self.guest_client.get(
            reverse('add_comment', args=('SitdikovR', 1)), follow=True)
        self.assertRedirects(response, reverse('login') + '?next=' +
                             reverse('add_comment',
                                     kwargs={'username': self.user.username,
                                             'post_id': self.post.id}))
