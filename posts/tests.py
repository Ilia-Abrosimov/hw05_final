from django.contrib.auth.models import User
from django.test import TestCase, Client
from posts.models import Post, Group, Follow
from django.urls import reverse
from django.core.cache import cache


class CreateUserTest(TestCase):
    name = 'AuthTestUser'

    def create_post(self, text, group, author):
        return(Post.objects.create(
            text=text,
            group=group,
            author=author
        ))

    def setUp(self):
        self.auth_client = Client()
        self.not_Auth_client = Client()
        self.auth_user = User.objects.create_user(
            username=self.name
        )
        self.auth_client.force_login(self.auth_user)
        self.group = Group.objects.create(
            title='This is test group',
            slug='test_group',
            description='Some description'
        )

    def test_personal_page(self):
        response = self.auth_client.get(
            reverse('profile', kwargs={'username': self.name})
        )
        self.assertEqual(response.status_code, 200)

    def test_auth_user_make_post(self):
        self.post = self.auth_client.post(reverse('new_post'),
                                          data={'text': 'This is test post',
                                                "group": self.group.id})
        self.assertTrue(Post.objects.filter(text='This is test post').exists())

    def test_not_auth_user_make_post(self):
        response = self.not_Auth_client.post(
            reverse('new_post'), kwargs={'text': 'This is test post',
                                         "group": self.group.id})
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200,
                             msg_prefix='', fetch_redirect_response=True)

    def check_pages(self, url, text, user, group):

        response = self.auth_client.get(url)
        if 'paginator' in response.context:
            current_post = response.context['paginator'].object_list.first()
        else:
            current_post = response.context['post']
        self.assertEqual(current_post.text, text)
        self.assertEqual(current_post.group, group)
        self.assertEqual(current_post.author, user)

    def test_check_made_post(self):
        post = self.create_post(text='This is test post', group=self.group,
                                author=self.auth_user)

        for url in (reverse('index'),
                    reverse('profile', kwargs={'username': self.name}),
                    reverse('post', kwargs={'username': self.name,
                                            'post_id': post.id})):

            self.check_pages(url=url, text='This is test post',
                             user=self.auth_user, group=self.group)

    def test_post_edit(self):
        post = self.create_post(text='This is test post', group=self.group,
                                author=self.auth_user)

        self.auth_client.get(
            reverse('post_edit', kwargs={'username': self.name,
                                         'post_id': post.id})
        )
        post.text = 'Changed text'
        post.save()
        for url in (reverse('index'),
                    reverse('profile', kwargs={'username': self.name}),
                    reverse('post', kwargs={'username': self.name,
                                            'post_id': post.id})):
            cache.clear()
            self.check_pages(url=url, text='Changed text',
                             user=self.auth_user, group=self.group)


class HW05Test(TestCase):
    name = 'AuthTestUser'

    def create_post(self, text, group, author):
        return (Post.objects.create(
            text=text,
            group=group,
            author=author
        ))

    def setUp(self):
        self.auth_client = Client()
        self.auth_user = User.objects.create_user(username=self.name)
        self.auth_client.force_login(self.auth_user)
        self.auth_client_follower = Client()
        self.auth_user_follower = User.objects.create_user(username='Follower')
        self.auth_client_follower.force_login(self.auth_user_follower)
        self.group = Group.objects.create(
            title='This is test group',
            slug='test_group',
            description='Some description'
        )

    def test_page_not_found(self):
        response = self.auth_client.get('wrong_page')
        self.assertEqual(response.status_code, 404)

    def test_pictures(self):
        with open('media/posts/file.jpg', 'rb') as img:
            post = self.create_post(text='post with image', group=self.group,
                                    author=self.auth_user)
            post.image.save(img.name, img)
            response = self.auth_client.get(reverse
                                            ('post',
                                             kwargs={'username': self.name,
                                                     'post_id': post.id}))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<img')

    def test_3pages(self):
        with open('media/posts/file.jpg', 'rb') as img:
            post = self.create_post(text='post with image', group=self.group,
                                    author=self.auth_user)
            post.image.save(img.name, img)
            for url in (reverse('index'),
                        reverse('profile', kwargs={'username': self.name}),
                        reverse('group', kwargs={'slug': self.group.slug})):
                cache.clear()
                response = self.auth_client.get(url)
                self.assertContains(response, '<img')

    def test_upload_wrong_file(self):
        with open('media/posts/wrong.txt', 'rb') as img:
            response = self.auth_client.post(reverse('new_post'),
                                             {'text': 'post with image',
                                              'group': self.group.id,
                                              'image': img},
                                             follow=True)
            self.assertNotContains(response, '<img')

    def test_cache(self):
        self.auth_client.post(
            reverse('new_post'),
            data={"text": "cache check", "group": self.group.id}, follow=True)
        response = self.auth_client.get(reverse('index'))
        self.assertContains(response, "cache check")
        self.auth_client.post(
            reverse('new_post'),
            data={"text": "2nd cache check",
                  "group": self.group.id}, follow=True)
        response = self.auth_client.get(reverse('index'))
        self.assertNotContains(response, "2nd cache check")

    def test_auth_user_subscribe_unsubscribe(self):
        before_subscribe = Follow.objects.count()
        self.auth_client_follower.get(
            reverse('profile_follow',
                    kwargs={'username': self.name}),
            data={'username': self.auth_user_follower.username})
        after_subscribe = Follow.objects.count()
        self.assertEqual(before_subscribe + 1, after_subscribe)
        self.auth_client_follower.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.name}),
            data={'username': self.auth_user_follower.username})
        after_unsubscribe = Follow.objects.count()
        self.assertEqual(before_subscribe, after_unsubscribe)

    def test_check_subscribe(self):
        self.auth_client_notfollower = Client()
        self.auth_user_notfollower = User.objects.\
            create_user(username='Notfollower')
        self.auth_client_notfollower.force_login(self.auth_user_notfollower)

        self.auth_client_follower.get(
            reverse('profile_follow',
                    kwargs={'username': self.name}),
            data={'username': self.auth_user_follower.username})

        self.auth_client.post(
            reverse('new_post'),
            data={"text": "Test post", "group": self.group.id}, follow=True)

        response_follower = self.auth_client_follower.\
            get(reverse('follow_index'))
        self.assertContains(response_follower, "Test post")
        response_notfollower = self.auth_client_notfollower.\
            get(reverse('follow_index'))
        self.assertNotContains(response_notfollower, "Test post")

    def test_comment(self):
        post = self.create_post(text='This is test post', group=self.group,
                                author=self.auth_user)

        self.auth_client.post(
            reverse('add_comment',
                    kwargs={'username': self.name, 'post_id': post.id}),
            data={'text': 'Test comment'})
        response = self.auth_client.get(reverse('post',
                                                kwargs={'username': self.name,
                                                        'post_id': post.id}))
        self.assertContains(response, "Test comment")
