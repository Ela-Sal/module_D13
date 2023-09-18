from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Post, PostCategory
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_about_new_post(sender, instance, **kwargs):

    if kwargs['action'] == 'post_add':
        categories = instance.postCategory.all()
        for category in categories:
            subscribers = category.subscribers.all()
       # subscribers = instance.category.values('subscribers__email', 'subscribers__username')

            # Отправляем письмо каждому подписчику
            for subscriber in subscribers:
                html_content = render_to_string(
                    'subscribe_mail.html',
                    {
                        'category': category,
                        'title': instance.title,
                        'text': instance.text

                    }
                )
                msg = EmailMultiAlternatives(
                    subject={category},
                    body='',
                    from_email='managernewssk@mail.ru',
                    to=[subscriber.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()