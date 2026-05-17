from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .models import Task

@receiver(pre_save, sender=Task)
def _store_old_status(sender, instance, **kwargs):

    if instance.pk:
        try:
            old = Task.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Task.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Task)
def notify_owner_on_status_change(sender, instance, created, **kwargs):

    old_status = getattr(instance, "_old_status", None)
    new_status = instance.status


    if old_status == new_status:
        return


    owner = getattr(instance, "owner", None)
    if not owner or not getattr(owner, "email", None):
        return


    if instance.last_notified_status == new_status:
        return


    context = {
        "task": instance,
        "old_status": old_status,
        "new_status": new_status,
        "owner": owner,
    }

    subject = f'Изменён статус задачи: "{instance.title}"'
    text_body = render_to_string('emails/task_status_changed.txt', context)
    html_body = render_to_string('emails/task_status_changed.html', context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        to=[owner.email],
    )
    if html_body:
        msg.attach_alternative(html_body, "text/html")


    msg.send()


    Task.objects.filter(pk=instance.pk).update(last_notified_status=new_status)