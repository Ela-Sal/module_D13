import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from ...models import Category, Post, PostCategory, CategorySubscribe, User
from django.urls import reverse
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)

print('Hi')
# наша задача по выводу текста на экран
def send_week_mail():

    #  Your job processing logic here...
    #print('Hello')
    categories = Category.objects.all() # Получаем все категории




    for category in categories:
        category_posts = Post.objects.filter(
            postCategory__name=category,
            dateCreation__gte=timezone.now() - datetime.timedelta(week=1),
        )
        print(category_posts)
        articles = []
        for subscriber in category.subscribers.all():

            # Получаем статьи только для данного подписчика
            articles = list(category_posts)
            #articles = category_posts.filter(author__authorUser=subscriber)
        #subscribers = category.subscribers.all()
            # :
            # Генерируем HTML-контент для письма, включая список статей
            print(subscriber)
            print(articles)
            html_content = render_to_string(
                'week_mail.html',
                {
                    'subscriber': subscriber,
                    'articles': articles,
                }
            )

            # Отправляем письмо с гиперссылками на статьи
            msg = EmailMultiAlternatives(
                subject='Недельные объявления',
                body='',
                from_email='managernewssk@mail.ru',
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")  # Добавляем HTML-контент в качестве альтернативного формата
            msg.send()
            print(html_content)
            print(msg)



# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."


    def handle(self, *args, **options):

        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_week_mail,
            trigger=CronTrigger(week="*/1"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="send_week_mail",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )

        logger.info("Added job 'send_week_mail'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")

            scheduler.start()

        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")

            scheduler.shutdown()

            logger.info("Scheduler shut down successfully!")